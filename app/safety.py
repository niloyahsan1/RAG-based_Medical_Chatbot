def is_medical_advice(query):
    risky_keywords = [
        "treatment", "diagnosis", "medicine",
        "what should I take", "prescription"
    ]
    return any(word in query.lower() for word in risky_keywords)

def safe_response():
    return "⚠️ I cannot provide medical advice. Please consult a healthcare professional."