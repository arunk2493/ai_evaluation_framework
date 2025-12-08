
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

def call_gemini(prompt, model="gemini-pro"):
    if not API_KEY:
        return f"[MOCKED_RESPONSE] {prompt[:80]}"
    resp = genai.GenerativeModel(model).generate_content(prompt)
    return resp.text
