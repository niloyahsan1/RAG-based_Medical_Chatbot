# RAG-based Medical Chatbot

A lightweight medical information assistant built with Python, Streamlit, LangChain, and FAISS. The app retrieves relevant hospital knowledge from PDFs and answers user questions using a retrieval-augmented generation (RAG) workflow.

This project is designed to help patients and visitors get hospital-related information quickly, while also supporting a basic appointment booking flow.

## Features

- Streamlit-based web interface
- RAG pipeline for retrieving hospital information from PDF documents
- Document chunking and embedding with LangChain + Hugging Face embeddings
- FAISS vector search for relevant context retrieval
- Groq-powered response generation
- SQLite appointment booking and availability checks
- Safety checks to avoid unsafe or unsupported medical advice

## Project Structure

- `main.py` - Streamlit app entry point
- `app/` - application logic
  - `database.py` - appointment database operations
  - `ingest.py` - PDF ingestion and FAISS indexing
  - `rag_engine.py` - answer generation and safety checks
  - `retriever.py` - retrieval logic
  - `safety.py` - medical safety validation
- `documents/` - source PDF knowledge files
- `vectordb/` - FAISS vector database
- `requirements.txt` - Python dependencies

## Setup

1. Create and activate a virtual environment if needed.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Add your environment variables in a `.env` file:

   ```env
   GROQ_API_KEY=your_api_key_here
   ```

4. Build the vector database from the PDF files:

   ```bash
   python app/ingest.py
   ```

5. Run the app:

   ```bash
   streamlit run main.py
   ```

## Notes

- The app expects PDF documents in the `documents/` folder.
- The vector index is stored in `vectordb/`.
- Appointment data is stored in `appointments.db`.
- This project is still under active development and is intended as a functional prototype.

## Collaborators

- [**Niloy Ahsan**](https://github.com/niloyahsan1)
- [**Tanay Paul**](https://github.com/tanay-official)