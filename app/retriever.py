import os
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


DB_PATH = "vectordb"


def ensure_vector_db_exists():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            "Vector database not found. Run 'python app/ingest.py' to build the FAISS index first."
        )


@lru_cache(maxsize=1)
def get_retriever(k=8):
    ensure_vector_db_exists()
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    db = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)

    return db.as_retriever(search_kwargs={"k": k})