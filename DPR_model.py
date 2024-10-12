from transformers import DPRQuestionEncoder, DPRContextEncoder, DPRContextEncoderTokenizer, DPRQuestionEncoderTokenizer
import torch
from langchain.schema import HumanMessage
from model import llm
import numpy as np


# Load the DPR question encoder and tokenizer
query_encoder = DPRQuestionEncoder.from_pretrained("facebook/dpr-question_encoder-single-nq-base")
query_tokenizer = DPRQuestionEncoderTokenizer.from_pretrained("facebook/dpr-question_encoder-single-nq-base")

# Load the DPR context encoder and tokenizer
passage_encoder = DPRContextEncoder.from_pretrained("facebook/dpr-ctx_encoder-single-nq-base")
passage_tokenizer = DPRContextEncoderTokenizer.from_pretrained("facebook/dpr-ctx_encoder-single-nq-base")

# Encode passages (transcripts) using the DPR context encoder
def encode_passages(videos_df):
    passages = videos_df['Transcript'].tolist()
    passage_embeddings = []

    for passage in passages:
        inputs = passage_tokenizer(passage, return_tensors='pt', max_length=512, truncation=True, padding=True)
        with torch.no_grad():
            embedding = passage_encoder(**inputs).pooler_output
        passage_embeddings.append(embedding.numpy())

    # Convert to a numpy array
    passage_embeddings = np.vstack(passage_embeddings)

    return passage_embeddings

# Function to encode the query and search for the most relevant passages
def search_relevant_passages(query, faiss_index, videos_df, top_k=3):
    query_inputs = query_tokenizer(query, return_tensors='pt', max_length=128, truncation=True, padding=True)

    with torch.no_grad():
        query_embedding = query_encoder(**query_inputs).pooler_output.numpy()
    query_embedding = query_embedding.reshape(1, -1)

    distances, indices = faiss_index.search(query_embedding, top_k)

    retrieved_passages = []
    for i in range(top_k):
        idx = indices[0][i]
        retrieved_passages.append({
            'Title': videos_df.iloc[idx]['Title'],
            'Transcript': videos_df.iloc[idx]['Transcript'],
            'Similarity Score': distances[0][i]
        })
    return retrieved_passages

# Function to retrieve relevant passages and generate an answer
def search_and_answer(query, faiss_index, videos_df, top_k=3):
    retrieved_passages = search_relevant_passages(query, faiss_index, videos_df, top_k)
    
    context = " ".join([passage['Transcript'] for passage in retrieved_passages])
    
    input_prompt = f"Question: {query}\nContext: {context} if there is different language rather than english than just you understand and given deafult answer ing english language.\nAnswer:"
    
    llm_response = llm([HumanMessage(content=input_prompt)])

    return llm_response.content

