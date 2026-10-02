
def is_medical_advice(query):
    text = (query or "").lower().strip()
    if not text:
        return False

    risky_keywords = [
        "diagnosis", "diagnose", "prescription", "prescribe", "medicine",
        "medication", "treatment plan", "what should i take", "what medicine",
        "which medicine", "symptom treatment", "treatment for", "medicine for",
        "what drug", "what tablet", "what antibiotic", "what injection",
        "how to cure", "home remedy", "self medicate"
    ]

    for keyword in risky_keywords:
        if keyword in text:
            return True

    medical_signals = [
        "fever", "infection", "pain", "cough", "sore throat", "headache",
        "chest pain", "shortness of breath", "disease", "illness",
        "symptom", "symptoms"
    ]

    if any(signal in text for signal in medical_signals):
        if any(word in text for word in [
            "what should", "what can", "how to treat", "what is the best",
            "should i take", "can i take"
        ]):
            return True

    return False


def safe_response():
    return "I cannot provide medical advice. Please consult a healthcare professional."