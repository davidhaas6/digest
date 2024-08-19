from __future__ import unicode_literals
import argparse
from typing import List
import youtube_dl
import os
import processing
import json

def subtitles(youtube_urls: List[str]) -> List[processing.ProcessedTranscript]:
    if not os.path.exists('cache'):
        os.mkdir('cache')
    
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'subtitleslangs': ['en'],  
        'subtitlesformat': 'vtt',  
        'writeautomaticsub': True,  # download auto-generated subs
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
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Youtube Summarizer")
    parser.add_argument("video_url", help="Youtube video URL to pull transcript from")
    parser.add_argument("output_file", help="Path to the output file", default='out_transcript.json', nargs='?')
    args = parser.parse_args()

    transcript = subtitles([args.video_url])[0]

    with open(args.output_file, 'w') as file:
        json.dump(transcript.dict(), file, indent=4)
    
    print("\nTLDR:", transcript.video_analysis.tldr_summary)
    print("\nSummary:\n",transcript.video_analysis.detailed_comprehensive_summary)
    print('\nBias:\n', transcript.video_analysis.detailed_bias_examination)
    print("\nExerpts:")
    for exerpt in transcript.video_analysis.key_exerpts_long:
        print(f"- {exerpt}")
    print("\nInteresting Counterpoints:")
    for counterpoint in transcript.video_analysis.interesting_counterpoints:
        print(f"- {counterpoint}")
    print("\nKey Insights:")
    for insight in transcript.video_analysis.key_insights:
        print(f"- {insight}")
    print("\nSources used by author:")
    for source in transcript.video_analysis.sources_used_by_author:
        print(f"- {source}")
    print(f"\nFull transcript and analysis: {args.output_file}")

