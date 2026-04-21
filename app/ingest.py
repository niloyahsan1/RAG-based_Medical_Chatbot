from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os


DATA_PATH = "documents"
DB_PATH = "vectordb"


# Ingest pipeline to load, chunk, and build vector database
def load_docs():
    docs = []

    for file in os.listdir(DATA_PATH):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(DATA_PATH, file))
            docs.extend(loader.load())

    return docs


# Chunk documents into smaller pieces for embedding
def chunk_docs(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

    return splitter.split_documents(docs)


# Build vector database from chunks
def build_db(chunks):
    import os
    os.makedirs(DB_PATH, exist_ok=True)

    print("Building embeddings...")

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    print("Creating FAISS index...")
    db = FAISS.from_documents(chunks, embeddings)

    print("Saving database...")
    db.save_local(DB_PATH)

    print("Database saved successfully!")


if __name__ == "__main__":
    docs = load_docs()
    chunks = chunk_docs(docs)
    build_db(chunks)
    print("Vector DB built")