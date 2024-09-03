from __future__ import unicode_literals
import argparse
import subprocess
from typing import List
import youtube_dl
import os
import processing
import json
import re
from datetime import datetime

def subtitles_ydl(youtube_urls: List[str]) -> List[processing.ProcessedTranscript]:
    if not os.path.exists('cache'):
        os.mkdir('cache')
    
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'subtitleslangs': ['en'],  
        'subtitlesformat': 'vtt',  
        # 'writeautomaticsub': True,  # download auto-generated subs
        'outtmpl': 'cache/%(id)s.%(ext)s'
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(youtube_urls)
    
    # get all files in cache
    markdown_text = []
    for file in os.listdir('cache'):
        if file.endswith('.vtt'):
            try:
                markdown = processing.vtt_to_md(f'cache/{file}')
                markdown_text.append(markdown)
            except Exception as e:
                print(f"Error processing {file}: {e}")
            os.remove(f'cache/{file}')
    
    return markdown_text


def subtitles_go(youtube_urls: List[str]) -> List[str]:
    subtitles = []
    for url in youtube_urls:
        output = subprocess.check_output(f"yt --transcript {url}", shell=True, text=True)
        subtitles.append(output.strip())
    return subtitles


def extract_youtube_id(url):
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=|embed\/|v\/)?(?:shorts\/)?(?:(?!watch)[\w-]{11})(?:[^\s"\'<>]+)?'
    
    match = re.search(pattern, url)
    if match:
        # Extract the video ID part from the match object
        video_id = re.search(r'[\w-]{11}', match.group(0))
        return video_id.group(0) if video_id else None
    return None


def save_transcript(transcript_data: processing.ProcessedTranscript, video_url: str):
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(current_file_dir, 'out')
    os.makedirs(out_dir, exist_ok=True)

    output_file_name = extract_youtube_id(args.video_url) or datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(out_dir, output_file_name) + '.json'
    with open(out_path, 'w') as file:
        data = transcript_data.dict()
        data['url'] = args.video_url
        json.dump(data, file, indent=4)
    return out_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Youtube Summarizer")
    parser.add_argument("video_url", help="Youtube video URL to pull transcript from")
    parser.add_argument("-t", "--transcript", help="Only get the transcript", action="store_true")
    parser.add_argument("-y", "--youtube-dl", help="Use Python ydl implementation", action="store_true")
    args = parser.parse_args()

    if args.youtube_dl:
        subitles = subtitles_ydl([args.video_url])[0]
    else:
        subitles = subtitles_go([args.video_url])[0]


    llm_processor = processing.LanguageModelProcessor()
    transcript_data = llm_processor.sanitize(subitles)
    analysis = llm_processor.analyze_transcript(transcript_data.clean_transcript)
    transcript_data = processing.ProcessedTranscript(
        summary_short=transcript_data.summary_short, 
        clean_transcript=transcript_data.clean_transcript, 
        video_analysis=analysis
    )

    out_path = save_transcript(transcript_data, args.video_url)
    
    print("\nTLDR:", analysis.tldr_summary_final_draft)
    print("\nSummary:\n",analysis.detailed_comprehensive_summary)
    print('\nBias:\n', analysis.detailed_bias_examination)
    print("\nExerpts:")
    for exerpt in analysis.key_exerpts:
        print(f"- {exerpt}")
    print("\nInteresting Counterpoints:")
    for counterpoint in analysis.interesting_counterpoints:
        print(f"- {counterpoint}")
    print("\nKey Insights:")
    for insight in analysis.key_insights:
        print(f"- {insight}")
    print("\nSources used by author:")
    for source in analysis.sources_used:
        print(f"- {source}")
    print(f"\nFull transcript and analysis: {out_path}")

