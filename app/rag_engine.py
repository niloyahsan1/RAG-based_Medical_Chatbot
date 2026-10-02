import os
import re

from groq import Groq
from .retriever import get_retriever
from .safety import is_medical_advice, safe_response
from dotenv import load_dotenv


load_dotenv()


HOSPITAL_PROFILE = {
    "name": "Fictional Hospital",
}


HOSPITAL_KEYWORDS = [
    "hospital", "doctor", "doctors", "patient", "patients", "appointment",
    "book", "booking", "schedule", "department", "clinic", "nurse",
    "ward", "room", "visiting", "visit", "hours", "admission", "discharge",
    "surgery", "policy", "rights", "symptom", "symptoms", "condition",
    "consultation", "medication", "treatment", "illness", "disease",
    "infection", "fever", "pain", "health", "medical"
]


client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def is_valid_reason(text):
    prompt = f"""
    Determine if the following input is a valid medical reason for visiting a hospital.

    Input: "{text}"

    Rules:
    - Must describe a symptom, illness, or health concern
    - Reject random text, gibberish, or meaningless sentences
    - Reject unrelated sentences

    Answer ONLY:
    YES or NO
    """

    # Generate response from LLM
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    result = response.choices[0].message.content.strip().upper()
    return result == "YES"


def fallback_response():
    return """
    I am sorry, I couldn't find that information in the hospital guidelines.

    **You can try asking questions such as:**
    - What are visiting hours?
    - How does the admission process work?
    - What should I do before surgery?
    - What are patient rights?

    For medical advice or emergencies, please contact a healthcare professional.
    """


def get_fixed_hospital_fact(query):
    text = query.lower().strip()

    if any(item in text for item in [
        "which hospital",
        "what hospital",
        "hospital name",
        "what is the hospital name",
        "what is this hospital",
        "what hospital is this",
        "what is the name of the hospital"
    ]):
        return f"{HOSPITAL_PROFILE['name']}."

    return None


def is_hospital_related(query):
    cleaned = re.sub(r"[^a-z0-9\s]", " ", query.lower())
    words = set(cleaned.split())

    if not words:
        return False

    for keyword in HOSPITAL_KEYWORDS:
        if keyword in words:
            return True

    return False


# Main function to handle user queries
def ask(query, history, appointments):
    query_lower = query.lower()

    fixed_fact = get_fixed_hospital_fact(query_lower)
    if fixed_fact is not None:
        return fixed_fact, []

    greetings = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}
    if query_lower.strip() in greetings:
        return "Hello! I can help with hospital guidelines, visiting hours, doctors, and appointments.", []

    if not is_hospital_related(query):
        return "Please ask only about the hospital.", []


    # Check for non-medical queries
    non_medical = {
        "what can you do": """I can help answer questions about hospital guidelines and procedures. 
                            
        You can try asking:

        - What are visiting hours?
        - How does the admission process work?
        - What should I do before surgery?
        - What are patient rights?

        For medical advice or emergencies, please contact a healthcare professional.""",


        "who are you": """I am the Fictional Hospital assistant.

        I can help you with:
        - Hospital policies
        - Admission and discharge procedures
        - Visiting guidelines
        - General patient information

        How can I assist you today?""",


        "what is your purpose": """My purpose is to help patients and caregivers access hospital information easily.

        You can ask about:
        - Admission process
        - Visiting hours
        - Surgery preparation
        - Patient rights""",

        "really": "Yes, I can help with that! Just ask me any questions you have about hospital policies, procedures, or general information.",
        "are you there?": "Yes, I am here! How can I assist you?",
        "thanks": "You are welcome! Let me know if you need anything else.",
        "thank you": "You are welcome! I am here to help.",
        "ok": "Alright! Let me know if you have any other questions.",
        "okay": "Got it! Feel free to ask anything else.",
        "got it": "Great! Let me know if you need further assistance.",
        "cool": "Let me know if you have more questions.",
        "bye": "Goodbye! Take care and stay safe.",
        "goodbye": "Goodbye! Feel free to return if you need help.",
        "hmm": "If you have any questions about hospital guidelines or procedures, feel free to ask!",
        "no": "I understand. Is there anything else I can help you with?",
        "nah": "I understand. Is there anything else I can help you with?",
        "not really": "I understand. If you have any questions about hospital guidelines or procedures, feel free to ask!",
        "maybe later": "No problem! I am here whenever you need assistance with hospital guidelines or procedures.",
        }
    
    
    # Check if query matches any non-medical responses
    for key in non_medical:
        if key in query_lower:
            return non_medical[key], []

    if not is_hospital_related(query):
        return "Please ask only about the hospital.", []

    # Safety check for medical advice
    if is_medical_advice(query):
        return safe_response(), []


    # Search with the user's wording so policy queries are not biased toward doctors.
    retriever = get_retriever(k=8)
    docs = retriever.invoke(query_lower)


    # Fallback response if no relevant docs found
    if not docs or len(docs) == 0:
        return fallback_response(), []


    # Create prompt with retrieved context
    unique_texts = list(set([d.page_content for d in docs]))
    context = "\n\n".join(unique_texts)


    # Add conversation history
    history_text = ""
    for h in history:
        history_text += f"{h['role']}: {h['content']}\n"


    # Prompt
    prompt = f"""
    You are an information assistant for a hospital.

    Use the conversation history if relevant.
    If the question refers to previous messages, use that context.

    Do NOT guess.
    Answer only based on:
    1. Conversation history
    2. Retrieved hospital documents
    
    If unclear, ask for clarification.

    RULES:
    - Answer clearly and directly.
    - Use bullet points when listing information.
    - DO NOT say "according to the document" or mention context.
    - Use simple language for patients.
    - If answer not found, say: "I do not have that information."

    Conversation History:
    {history_text}

    Context:
    {context}

    User Question:
    {query}
    """

    # Generate response from LLM
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    answer = response.choices[0].message.content


    # Check for fallback in answer
    if "I do not have that information" in answer:
        return fallback_response(), docs

    return answer, docs