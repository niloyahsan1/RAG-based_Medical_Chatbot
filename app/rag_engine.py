import os
from groq import Groq
from .retriever import get_retriever
from .safety import is_medical_advice, safe_response
from dotenv import load_dotenv


load_dotenv()


client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def fallback_response():
    return """
    I'm sorry, I couldn't find that information in the hospital guidelines.

    **You can try asking questions such as:**

    - What are visiting hours?
    - How does the admission process work?
    - What should I do before surgery?
    - What are patient rights?

    For medical advice or emergencies, please contact a healthcare professional.
    """


def ask(query):
    query_lower = query.lower()

    # Simple greeting check
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]

    if any(greet in query_lower for greet in greetings):
        return "Hello! How can I assist you today?", []
    
    # Small talk responses
    small_talk = {
        "thanks": "You're welcome! Let me know if you need anything else.",
        "thank you": "You're welcome! I'm here to help.",
        "thank u": "You're welcome! I'm here to help.",
        "ok": "Alright! Let me know if you have any other questions.",
        "okk": "Alright! Let me know if you have any other questions.",
        "okay": "Got it! Feel free to ask anything else.",
        "okayy": "Got it! Feel free to ask anything else.",
        "got it": "Great! Let me know if you need further assistance.",
        "cool": "Let me know if you have more questions.",
        "bye": "Goodbye! Take care and stay safe.",
        "byee": "Goodbye! Take care and stay safe.",
        "goodbye": "Goodbye! Feel free to return if you need help.",
        "goodbyee": "Goodbye! Feel free to return if you need help.",
        "oh": "Thanks for your understanding! Let me know if you have any other questions.",
        "ohh": "Thanks for your understanding! Let me know if you have any other questions.",
        "ohhh": "Thanks for your understanding! Let me know if you have any other questions.",
        "o": "Thanks for your understanding! Let me know if you have any other questions.",
        "oo": "Thanks for your understanding! Let me know if you have any other questions.",
        "ooo": "Thanks for your understanding! Let me know if you have any other questions.",
    }
    
    for key in small_talk:
        if key in query_lower:
            return small_talk[key], []


    # Safety check for medical advice
    if is_medical_advice(query):
        return safe_response(), []


    # Retrieve docs relevant to the query
    retriever = get_retriever(k=5)
    docs = retriever.invoke(query)


    # Fallback response if no relevant docs found
    if not docs or len(docs) == 0:
        return fallback_response(), []


    # Create prompt with retrieved context
    unique_texts = list(set([d.page_content for d in docs]))
    context = "\n\n".join(unique_texts)


    # Prompt
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


    # Generate response from LLM
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    answer = response.choices[0].message.content


    # Check for fallback in answer
    if "I do not have that information" in answer:
        return fallback_response(), docs

    return answer, docs