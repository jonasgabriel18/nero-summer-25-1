from pytube import Playlist

from langchain_community.document_loaders import YoutubeLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def load_transcripts(url: str) -> list[str]:
    playlist = Playlist(url)
    transcripts = []

    for video in playlist.video_urls:
        video_loader = YoutubeLoader.from_youtube_url(video)
        video_transcript = video_loader.load()

        if not video_transcript:
            continue

        transcripts.append(video_transcript[0])
    
    return transcripts

def create_and_save_vectorstore(urls, embedding):
    all_docs = []

    for url in urls:
        all_docs.extend(load_transcripts(url))
    
    vector_db = FAISS.from_documents(all_docs, embedding)

    vector_db.save_local("./vectorstore/nlp_cs_theory")

if __name__ == "__main__":

    urls = ["https://www.youtube.com/playlist?list=PLofp2YXfp7TZZ5c7HEChs0_wfEfewLDs7",
            "https://www.youtube.com/playlist?list=PLm3J0oaFux3ZYpFLwwrlv_EHH9wtH6pnX"
        ]

    embedding_size = 1536
    embedding_model = "text-embedding-3-small"
    embeddings = OpenAIEmbeddings(model=embedding_model, dimensions=embedding_size)

    create_and_save_vectorstore(urls, embeddings)