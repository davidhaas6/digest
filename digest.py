from __future__ import unicode_literals
import argparse
import subprocess
from typing import List
import youtube_dl
import os
import processing
import json


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



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Youtube Summarizer")
    parser.add_argument("video_url", help="Youtube video URL to pull transcript from")
    parser.add_argument("output_file", help="Path to the output file", default='out_transcript.json', nargs='?')
    parser.add_argument("-t", "--transcript", help="Only get the transcript", action="store_true")
    parser.add_argument("-y", "--youtube-dl", help="Use Python ydl implementation", action="store_true")
    args = parser.parse_args()

    if args.youtube_dl:
        transcripts = subtitles_ydl([args.video_url])
    else:
        transcripts = subtitles_go([args.video_url])
    text_transcript = transcripts[0]

    if args.transcript:
        print(text_transcript)
        exit(0)
    
    llm_processor = processing.LanguageModelProcessor()
    analysis = llm_processor.analyze_transcript(text_transcript)
    transcript_data = processing.ProcessedTranscript(summary_short='', clean_transcript=text_transcript, video_analysis=analysis)
    

    # transcript_data = processing.analyze_transcript(text_transcript)


    with open(args.output_file, 'w') as file:
        json.dump(transcript_data.dict(), file, indent=4)
    
    print("\nTLDR:", transcript_data.video_analysis.tldr_summary_final_draft)
    print("\nSummary:\n",transcript_data.video_analysis.detailed_comprehensive_summary)
    print('\nBias:\n', transcript_data.video_analysis.detailed_bias_examination)
    print("\nExerpts:")
    for exerpt in transcript_data.video_analysis.key_exerpts:
        print(f"- {exerpt}")
    print("\nInteresting Counterpoints:")
    for counterpoint in transcript_data.video_analysis.interesting_counterpoints:
        print(f"- {counterpoint}")
    print("\nKey Insights:")
    for insight in transcript_data.video_analysis.key_insights:
        print(f"- {insight}")
    print("\nSources used by author:")
    for source in transcript_data.video_analysis.sources_used:
        print(f"- {source}")
    print(f"\nFull transcript and analysis: {args.output_file}")

