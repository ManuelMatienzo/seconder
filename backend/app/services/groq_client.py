import os

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY NO CARGADA")

    print("GROQ_API_KEY cargada correctamente")

    from groq import Groq
    return Groq(api_key=api_key)
