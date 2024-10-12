import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


def extract_video_id(youtube_url):
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', youtube_url)
    return video_id_match.group(1) if video_id_match else None

def extract_transcript(videos_df):
    """Fetches transcripts for each video in the DataFrame and updates the DataFrame."""
    # Initialize a new column for transcripts
    videos_df['Transcript'] = None

    # Iterate over each video and fetch the transcript
    for index, row in videos_df.iterrows():
        youtube_url = row['url']
        video_title = row['Title']
        video_id = extract_video_id(youtube_url)

        if video_id:
            try:
                # List available transcripts
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

                # Try to fetch the English transcript first
                try:
                    transcript = transcript_list.find_transcript(['en'])
                except:
                    # If English is not available, get the first available transcript
                    transcript = next(iter(transcript_list))

                transcript_text = " ".join([item['text'] for item in transcript.fetch()])
                print(f"Transcript for {video_title} (Language: {transcript.language}):")
                print(transcript_text)

                # Add the transcript to the DataFrame
                videos_df.at[index, 'Transcript'] = transcript_text

            except Exception as e:
                # Handle any errors (e.g., no transcript available)
                print(f"An error occurred for video '{video_title}' ({video_id}): {e}")
                videos_df.at[index, 'Transcript'] = None

    return videos_df



