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
    You are a medical information assistant.

    STRICT RULES:
    - Answer ONLY from the provided context.
    - If the answer is NOT clearly found → say EXACTLY:
    "I do not have that information."

    - DO NOT add extra knowledge.
    - DO NOT guess.
    - DO NOT continue after saying you don't know.

    Context:
    {context}

    Question:
    {query}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        # model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content, docs