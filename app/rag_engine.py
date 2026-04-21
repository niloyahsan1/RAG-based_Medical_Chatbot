import os
from turtle import st
from groq import Groq
from .retriever import get_retriever
from .safety import is_medical_advice, safe_response
from dotenv import load_dotenv


load_dotenv()


client = Groq(api_key=os.getenv("GROQ_API_KEY"))


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


# Main function to handle user queries
def ask(query):
    query_lower = query.lower()

    # Simple greeting check
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]

    if any(greet in query_lower for greet in greetings):
        return "Hello! How can I assist you today?", []
    
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


    # Safety check for medical advice
    if is_medical_advice(query):
        return safe_response(), []


    # Retrieve docs relevant to the query
    retriever = get_retriever(k=2)
    docs = retriever.invoke(query)


    # Fallback response if no relevant docs found
    if not docs or len(docs) == 0:
        return fallback_response(), []


    # Create prompt with retrieved context
    unique_texts = list(set([d.page_content for d in docs]))
    context = "\n\n".join(unique_texts)


    history = st.session_state.chat_history[-4:]  # last few messages
    history_text = ""
    for h in history:
        history_text += f"{h['role']}: {h['content']}\n"


    # Prompt
    prompt = f"""
    You are a medical assistant for a hospital.

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
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    answer = response.choices[0].message.content


    # Check for fallback in answer
    if "I do not have that information" in answer:
        return fallback_response(), docs

    return answer, docs