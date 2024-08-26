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
    transcript_chapters: List[str]
    key_exerpts: List[str]
    key_insights: List[str]
    sources_used: List[str]
    detailed_bias_examination: str
    tldr_summary_final_draft: str
    interesting_counterpoints: List[str]


class ProcessedTranscript(BaseModel):
    summary_short: str
    clean_transcript: str
    video_analysis: Analysis


class Transcript(BaseModel):
    summary_short: str
    clean_transcript: str


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

    def process(self, text: str) -> ProcessedTranscript:
        pass

    def sanitize_analyze(self, text: str) -> ProcessedTranscript:
        def api_call():
            return self.client.beta.chat.completions.parse(
                messages=[
                    {
                        "role": "system",
                        "content": """Your job is to convert video subtitles to nicely formatted transcripts. The input subtitles contain missing punctuation, transcription errors, and other artifacts that you must clean. Some words in the subtitles may be incorrect due to transcription errors, which you should selectively fix given the context of the video. The clean transcript should be well-formatted and accurately contain all of the spoken content. In addition to the transcript, you will analyze content from the video to aid the user's understanding.
    
                        
                        ## Analysis:

                        Each component of the analysis must be rooted in the video's transcript. You must frequently embed quotes from the video into relevant parts of the analysis. 

                        The "detailed_comprehensive_summary" is a comprehensive and engaging 800-word summary, aiming to provide the user the experience of watching the video through mirroring the style, and pacing of the video's transcript. It must embed at least 10 quotes from the video.

                        The "key_exerpts" should be direct quotes from the video transcript that are insightful and help contextualize the content for the user.
                    
                        
                        # Task:

                        Output a JSON object containing a short summary of the video, the clean transcript, and an analysis of the video. It is crucial the clean transcript is accurate and high-quality. 
                        """,
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
        completion = util.run_with_progress(api_call, estimated_time)
        output: ProcessedTranscript = completion.choices[0].message.parsed

        num_letters_in = len(re.findall(r'[a-zA-Z]', text))
        num_letters_out = len(re.findall(r'[a-zA-Z]', output.clean_transcript))
        print("Input length:", num_letters_in, "letters. Cleaned transcript length:", num_letters_out, "letters")

        return output
    

    def sanitize(self, subtitles: str) -> Transcript:
        def llm_clean():
            return self.client.beta.chat.completions.parse(
                messages=[
                    {
                        "role": "system",
                        "content": """Your job is to convert video subtitles to nicely formatted transcripts. The input subtitles contain missing punctuation, transcription errors, and other artifacts that you must clean. Some words in the subtitles may be incorrect due to transcription errors, which you should selectively fix given the context of the video. The clean transcript should be well-formatted and accurately contain all of the spoken content.
    
                        
                        # Task:

                        Output a JSON object containing a short summary of the video, the clean transcript. It is crucial the clean transcript is accurate, complete, and high-quality. 
                        """,
                    },
                    {
                        "role": "user",
                        "content": subtitles,
                    }
                ],
                response_format=Transcript,
                temperature=0,
                top_p=.95,
                model="gpt-4o-mini",
            )
        
        estimated_time = self._estimate_processing_time(subtitles)
        completion = util.run_with_progress(llm_clean, estimated_time)
        output: Transcript = completion.choices[0].message.parsed
        return output

    def analyze_transcript(self, transcript: str) -> Analysis:
        """Extract summaries, insights, and other data from a transcript
        
        """
        def llm_analyze():
            return self.client.beta.chat.completions.parse(
                messages=[
                    {
                        "role": "system",
                        "content": """Your job is to summarize and analyze transcripts to help someone understand its content. Your analysis must be thorough, insightful, and embed quotes from the transcript.
                        

                        ## Analysis Components:
                        The different components of the analysis are described by the name of their JSON key. These components have more detailed descriptions:

                         - The "detailed_comprehensive_summary" is a 800-word summary of the video that accurately captures its content, style, and progression. Begin with a brief (50-word) analysis of the video's structure and main themes. Then, organize the main body (650 words) either chronologically, thematically, or using a combination of both approaches as appropriate for the video's content. Ensure even coverage by including at least 2-3 key points or themes from each quarter of the video's runtime. For each main point or theme, summarize it concisely in your own words, include a relevant word-for-word quote from the transcript (aim for at least 8 quotes total, distributed evenly throughout the summary), and indicate approximately when in the video this point or theme is discussed. Throughout the summary, mirror the video's original style, tone, and pacing, incorporating similar presentation techniques or rhetorical devices where appropriate. Conclude with a brief (100-word) overview that encapsulates the video's main message, its significance, and how its structure contributed to its overall impact. Your summary should provide readers with a comprehensive understanding of the video's content, progression, and style, as if they had watched the full video themselves.

                         - The "key_exerpts" should be direct quotes from the transcript that are insightful and help contextualize its content.
                    
                        
                        # Task:
                        Output a JSON object containing a full analysis of the transcript.
                        """,
                    },
                    {
                        "role": "user",
                        "content": transcript,
                    }
                ],
                response_format=Analysis,
                temperature=0.3,
                model="gpt-4o-2024-08-06",
            )
        
        estimated_time = self._estimate_processing_time(transcript) * .5
        completion = util.run_with_progress(llm_analyze, estimated_time)
        output: Analysis = completion.choices[0].message.parsed
        return output

    def _count_tokens(self, text: str) -> int:
        encoder = tiktoken.encoding_for_model("gpt-4o-mini")
        tokens = encoder.encode(text)
        return len(tokens)
    
    def _estimate_processing_time(self, text: str) -> float:
        token_count = self._count_tokens(text)
        print(token_count, 'tokens')
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

    return markdown_output


def analyze_transcript(subtitles: str) -> ProcessedTranscript:
    llm_processor = LanguageModelProcessor()
    processed_transcript = llm_processor.sanitize_analyze(subtitles)
    return processed_transcript
