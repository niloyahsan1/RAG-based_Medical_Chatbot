# Fictional Hospital Assistant
A hospital-focused chatbot built with Streamlit, FAISS, and a retrieval-augmented generation pipeline. The app is designed to answer hospital-related questions, explain services and policies, suggest relevant doctors, and help users with appointment booking in a fictional healthcare setting.

This project is intentionally scoped to hospital information rather than general-purpose medical advice. It is meant to support patient and visitor queries in a controlled environment.

## What this project does
- Answers hospital-related questions using retrieved knowledge from local documents
- Helps users understand hospital processes and services
- Supports appointment-related conversations and booking flow
- Shows doctor-related information based on hospital documents
- Includes safety checks to keep the assistant within its intended scope

## How it works
1. Hospital documents are loaded from the `documents/` folder.
2. The content is split into smaller chunks for better retrieval.
3. These chunks are embedded using Hugging Face models.
4. The embeddings are stored in a FAISS vector database under `vectordb/`.
5. When a user asks a question, the app retrieves the most relevant document chunks.
6. The retrieved context is passed to a Groq-powered language model.
7. The assistant responds with a hospital-focused answer, while keeping the experience safe and limited to the project scope.

## Project structure
```text
RAG-based_Medical_Chatbot/
├── .env
├── .gitignore
├── app/
│   ├── database.py
│   ├── ingest.py
│   ├── rag_engine.py
│   ├── retriever.py
│   ├── safety.py
│   ├── static/
│   │   └── styles.css
│   └── templates/
│       └── chat_message.html
├── documents/
├── vectordb/
│   ├── index.faiss
│   └── index.pkl
├── main.py
├── appointments.db
├── README.md
└── requirements.txt
```

## Features
- Streamlit-based hospital assistant interface
- Retrieval-augmented generation using FAISS
- Hospital-specific query handling
- SQLite-based appointment storage
- Doctor and appointment flow for patients
- Safety filtering for unsuitable or out-of-scope requests

## Setup
Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

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

## Notes
- The project is built for a fictional hospital context.
- The assistant is not a general healthcare advisor.
- For urgent medical issues, the user should contact emergency services or a licensed medical professional.

## Collaborators
- [Niloy Ahsan](https://github.com/niloyahsan1)
- [Tanay Paul](https://github.com/tanay-official)
