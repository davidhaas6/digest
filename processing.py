from typing import List, Dict
import re
import os
from pydantic import BaseModel
from openai import OpenAI
import tiktoken
import time
import util

class Analysis(BaseModel):
    detailed_comprehensive_summary: str
    tldr_summary: str
    video_section_titles: List[str]
    key_insights: List[str]
    key_exerpts_long: List[str]
    sources_used_by_author: List[str]
    detailed_bias_examination: str
    interesting_counterpoints: List[str]


class ProcessedTranscript(BaseModel):
    summary_short: str
    clean_transcript: str
    video_analysis: Analysis


class VTTParser:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_file(self) -> str:
        with open(self.file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def parse_subtitles(self) -> List[Dict]:
        content = self.read_file()
        subtitle_blocks = re.split(r'\n\n+', content.strip())
        subtitles = []
        seen_texts = set()
        
        for block in subtitle_blocks[1:]:  # Skip the first block (WebVTT header)
            lines = block.split('\n')
            if len(lines) >= 2:
                timing = lines[0]
                text = ' '.join(lines[1:]).strip()
                if text and not text.startswith('align:'):  # Exclude empty or alignment-only entries
                    # Check for duplication
                    if text not in seen_texts:
                        subtitles.append({'timing': timing, 'text': text})
                        seen_texts.add(text)
        
        return subtitles


class TextSanitizer:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


    def clean_whitespace(self, text: str) -> str:
        return ' '.join(text.split())

    def add_punctuation(self, text: str) -> str:
        if text and not text[-1] in '.!?':
            text += '.'
        return text

    def fix_capitalization(self, text: str) -> str:
        return text[0].upper() + text[1:] if text else text

    def fix_profanity(self, text: str) -> str:
        return text.replace('[ __ ]', '[profanity]')
    

    def sanitize(self, subtitle: Dict) -> Dict:
        text = subtitle['text']
        text = self.clean_whitespace(text)
        text = self.add_punctuation(text)
        text = self.fix_capitalization(text)
        text = self.fix_profanity(text)
        text = text.replace('&nbsp;', '')
        subtitle['text'] = text
        return subtitle


class MarkdownConverter:
    def convert_to_markdown(self, subtitles: List[Dict]) -> str:
        markdown = "# Video Transcript\n\n"
        for subtitle in subtitles:
            markdown += f"{subtitle['text']} \n"
        
        return markdown.strip()


class LanguageModelProcessor:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def llm_sanatize(self, text: str) -> ProcessedTranscript:
        print("Querying LLM...")
        def api_call():
            return self.client.beta.chat.completions.parse(
                messages=[
                    {
                        "role": "system",
                        "content": "Your job is to convert video subtitles to nicely formatted transcripts. The input subtitles contain missing punctuation, transcription errors, and other artifacts that you must clean. Some words in the subtitles may be incorrect due to transcription errors, which you should selectively fix given the context of the video. The clean transcript should be well-formatted and accurately contain all of the spoken content.\n\nYou should output a JSON containing a short summary of the video, the cleaned transcript, and a thorough analysis of the video.",
                    },
                    {
                        "role": "user",
                        "content": text,
                    }
                ],
                response_format=ProcessedTranscript,
                temperature=0,
                model="gpt-4o-mini",
            )
        
        estimated_time = self._estimate_processing_time(text)
        print ("Estimated processing time:", estimated_time, "seconds")
        start = time.time()

        completion = util.run_with_progress(api_call, estimated_time)
        output: ProcessedTranscript = completion.choices[0].message.parsed

        end = time.time()
        num_letters_in = len(re.findall(r'[a-zA-Z]', text))
        num_letters_out = len(re.findall(r'[a-zA-Z]', output.clean_transcript))
        print("Actual processing time:", round(end-start), "seconds\n")
        print("Input length:", num_letters_in, "letters. Cleaned transcript length:", num_letters_out, "letters")

        return output

    def _count_tokens(self, text: str) -> int:
        encoder = tiktoken.encoding_for_model("gpt-4o-mini")
        tokens = encoder.encode(text)
        return len(tokens)
    
    def _estimate_processing_time(self, text: str) -> float:
        token_count = self._count_tokens(text)
        tps_estimates = [183, 112, 80, 140, 100]
        tokens_per_s = sum(tps_estimates) / len(tps_estimates)
        initial_estimate = token_count / tokens_per_s
        initial_estimate *= 2  # Account for both input/output tokens

        return round(initial_estimate)


def vtt_to_md(input_file) -> ProcessedTranscript:
    vtt_parser = VTTParser(input_file)
    raw_subtitles = vtt_parser.parse_subtitles()

    sanitizer = TextSanitizer()
    sanitized_subtitles = [sanitizer.sanitize(subtitle) for subtitle in raw_subtitles]

    md_converter = MarkdownConverter()
    markdown_output = md_converter.convert_to_markdown(sanitized_subtitles)

    llm_processor = LanguageModelProcessor()
    processed_transcript = llm_processor.llm_sanatize(markdown_output)

    return processed_transcript

