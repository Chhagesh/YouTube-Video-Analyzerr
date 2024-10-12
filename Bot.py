import streamlit as st
from function import fetch_youtube_videos
from transcript import extract_transcript
from DPR_model import encode_passages, search_and_answer
import faiss
import numpy as np
import pandas as pd

def initialize_faiss_index(videos_df):
    passage_embeddings = encode_passages(videos_df)
    dimension = passage_embeddings.shape[1]
    faiss_index = faiss.IndexFlatIP(dimension)
    faiss_index.add(passage_embeddings)
    return faiss_index

def main():
    st.set_page_config(page_title="YouTube Video Analyzer", page_icon="🎥", layout="wide")
    st.title("🎥 YouTube Video Analyzer For Traveling")

    with st.sidebar:
        st.header("🔍 Search Options")
        search_query = st.text_input("Enter your Destination:", placeholder="e.g., India, Mumbai, New York")
        topics = st.multiselect("Select topics:", ["culture", "food", "adventure", "history", "nature"])
        num_videos = st.number_input("Number of videos to fetch:", min_value=1, max_value=25, value=3)
        min_views = st.number_input("Minimum views:", min_value=0, value=10000, step=10000)
        if st.button("Fetch Videos"):
            if search_query and topics:
                with st.spinner("Fetching videos..."):
                    progress_bar = st.progress(0)
                    videos = fetch_youtube_videos(search_query, topics, min_views, num_videos)
                    progress_bar.progress(50)
                    videos_df = pd.DataFrame(videos)
                    videos_df = extract_transcript(videos_df)
                    print(videos_df)
                    progress_bar.progress(100)
                
                # Filter out videos without transcripts
                videos_df = videos_df.dropna(subset=['Transcript'])
                
                if videos_df.empty:
                    st.warning("No videos with transcripts found. Please try a different search.")
                else:
                    st.session_state['videos_df'] = videos_df
                    faiss_index = initialize_faiss_index(videos_df)
                    st.session_state['faiss_index'] = faiss_index
                    st.success("Videos fetched successfully!")

    # Question answering section
    st.header("❓ Ask Questions")
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_query := st.chat_input("Ask a question about the videos:"):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
        
        if 'videos_df' in st.session_state and 'faiss_index' in st.session_state:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = search_and_answer(user_query, st.session_state['faiss_index'], st.session_state['videos_df'], top_k=3)
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            st.info("Fetch videos first to ask questions about them.")

    # Display YouTube videos side by side
    if 'videos_df' in st.session_state:
        st.header("📺 Fetched YouTube Videos")
        videos_df = st.session_state['videos_df']
        cols = st.columns(3)  # Adjust the number of columns as needed
        for index, row in videos_df.iterrows():
            with cols[index % 3]:
                with st.expander(row['Title']):
                    st.write(f"Views: {row['Views']}")
                    st.write(f"Duration: {row['Duration']}")
                    st.video(row['url'])

if __name__ == "__main__":
    main()
