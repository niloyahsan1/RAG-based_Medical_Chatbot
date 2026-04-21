from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


DB_PATH = "vectordb"

def get_retriever(k=2):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    db = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)

    return db.as_retriever(search_kwargs={"k": k})