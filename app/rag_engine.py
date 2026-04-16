import os
from groq import Groq
from .retriever import get_retriever
from .safety import is_medical_advice, safe_response

from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask(query):
    if is_medical_advice(query):
        return safe_response(), []

    retriever = get_retriever(k=3)
    docs = retriever.invoke(query)

    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
    You are a medical assistant for a hospital.

    RULES:
    - Answer clearly and directly.
    - Use bullet points when listing information.
    - DO NOT say "according to the document" or mention context.
    - Use simple language for patients.
    - If answer not found, say: "I do not have that information."

    Context:
    {context}

    Question:
    {query}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",   # or your working model
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content, docs