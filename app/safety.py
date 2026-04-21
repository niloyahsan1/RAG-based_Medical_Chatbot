
def is_medical_advice(query):
    risky_keywords = ["treatment", "diagnosis", "medicine", "what should I take", "prescription"]
    
    for word in risky_keywords:
        if word in query.lower():
            return True
        
    return False


def safe_response():
    return "I cannot provide medical advice. Please consult a healthcare professional."