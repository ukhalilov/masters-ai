# app/data_ingestion.py

from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def load_documents(data_dir):
    docs = []
    for file in os.listdir(data_dir):
        path = os.path.join(data_dir, file)
        if file.endswith(".pdf"):
            loader = PyPDFLoader(path)
            pages = loader.load_and_split()
            for i, page in enumerate(pages):
                page.metadata["source"] = f"{file} - page {i + 1}"
            docs.extend(pages)
        elif file.endswith(".txt"):
            loader = TextLoader(path, encoding="utf-8")
            content = loader.load()
            for doc in content:
                doc.metadata["source"] = file
            docs.extend(content)
    return docs

def ingest_to_faiss(docs, store_dir="vector_store"):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings()  # You can switch to SentenceTransformerEmbeddings
    db = FAISS.from_documents(split_docs, embeddings)
    db.save_local(store_dir)
    print(f"✅ Indexed {len(split_docs)} chunks into {store_dir}/")

if __name__ == "__main__":
    docs = load_documents("data")
    ingest_to_faiss(docs)
