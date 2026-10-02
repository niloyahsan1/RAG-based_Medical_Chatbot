# RAG-based Medical Chatbot

A Streamlit-based hospital assistant that answers medical and hospital-related questions using a retrieval-augmented generation (RAG) system. The application reads hospital knowledge from PDF documents, converts them into embeddings, stores them in a FAISS vector database, retrieves the most relevant chunks for a query, and then generates a response using Groq LLMs. It also includes a basic appointment booking flow for patients.

## How it works

1. PDF documents are loaded from the `documents/` folder.
2. The documents are split into smaller chunks.
3. Each chunk is converted into embeddings using Hugging Face sentence-transformers.
4. The embeddings are stored in a FAISS vector database under `vectordb/`.
5. When a user asks a question, the app retrieves the most relevant chunks from the database.
6. The retrieved context is combined with the user query and passed to the Groq-powered LLM.
7. The model generates a response based on the hospital information in the retrieved context.
8. The app also validates the query for safety and supports appointment booking through SQLite.

## Project Structure
```text
RAG-based_Medical_Chatbot/
├── app/
│   ├── database.py
│   ├── ingest.py
│   ├── rag_engine.py
│   ├── retriever.py
│   └── safety.py
├── documents/
├── vectordb/
├── .env
├── .gitignore
├── appointments.db
├── main.py
├── README.md
├── requirements.txt
└── template.sh
```

## Features
- Streamlit interface for user interaction
- PDF-based knowledge retrieval using RAG
- Semantic search with FAISS
- LLM-based response generation with Groq
- Appointment booking and doctor availability checks
- Safety checks for medical queries

## Setup
```bash
pip install -r requirements.txt
```

Create a `.env` file and add:
```env
GROQ_API_KEY=your_api_key_here
```

Build the vector database:
```bash
python app/ingest.py
```

Run the app:
```bash
streamlit run main.py
```

## Collaborators
- [**Niloy Ahsan**](https://github.com/niloyahsan1)
- [**Tanay Paul**](https://github.com/tanay-official)