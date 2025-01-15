from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.documents import Document
from typing import List, Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from langchain_community.vectorstores import FAISS

from dotenv import load_dotenv
from operator import itemgetter 
import os

from tqdm import tqdm

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
    You're an AI assistant that will answer questions about natural language processing and computer science theory.

    Besides, here is some extra content about natural language processing and/or computer science theory:

    [extra content]
    {extra_content}
    [End of extra content]

    --------------------------------------------
    """

def load_vdb_and_retriever(path="./nlp_cs_theory",
                           k=4):
    embedding_size = 1536
    embedding_model = "text-embedding-3-small"
    embeddings = OpenAIEmbeddings(model=embedding_model, dimensions=embedding_size)
    
    vdb = FAISS.load_local(path, 
                           embeddings, 
                           allow_dangerous_deserialization=True)
    
    retriever = vdb.as_retriever(search_kwargs={"k": k})
    
    return vdb, retriever

def format_docs(docs: List[Document]) -> str:
    return "\n".join([x.page_content for x in docs])

def create_chain():
    _, retriever = load_vdb_and_retriever()
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
        ]
    )

    chain = (
        {
            "input": RunnablePassthrough(),
            "extra_content": retriever | RunnableLambda(format_docs)
        }
        | prompt 
        | llm 
        | StrOutputParser()
    )

    return chain
