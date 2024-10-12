import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


def extract_video_id(youtube_url):
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', youtube_url)
    return video_id_match.group(1) if video_id_match else None

def extract_transcript(videos_df):
    """Fetches transcripts for each video in the DataFrame and updates the DataFrame."""
    videos_df['Transcript'] = None
    videos_df['Transcript_Language'] = None

    for index, row in videos_df.iterrows():
        youtube_url = row['url']
        video_title = row['Title']
        video_id = extract_video_id(youtube_url)

        if video_id:
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                # Priority order: Manual English, Auto-generated English, Any manual, Any auto-generated
                transcript_priorities = [
                    ('en', False),  # Manual English
                    ('en', True),   # Auto-generated English
                    (None, False),  # Any manual
                    (None, True)    # Any auto-generated
                ]

                for lang, is_generated in transcript_priorities:
                    try:
                        if lang:
                            transcript = transcript_list.find_transcript([lang])
                        else:
                            transcript = next(t for t in transcript_list if t.is_generated == is_generated)
                        
                        if transcript.is_generated != is_generated:
                            continue

                        transcript_text = " ".join([item['text'] for item in transcript.fetch()])
                        videos_df.at[index, 'Transcript'] = transcript_text
                        videos_df.at[index, 'Transcript_Language'] = transcript.language
                        print(f"Transcript found for {video_title} (Language: {transcript.language}, Auto-generated: {transcript.is_generated})")
                        break
                    except:
                        continue

                if videos_df.at[index, 'Transcript'] is None:
                    print(f"No suitable transcript found for {video_title}")

            except Exception as e:
                print(f"An error occurred for video '{video_title}' ({video_id}): {e}")

    return videos_df



