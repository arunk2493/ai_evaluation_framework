
import google.generativeai as genai
import os

# Read GEMINI_API_KEY directly from environment variables
API_KEY = os.getenv("GEMINI_API_KEY")
print(f"Using GEMINI_API_KEY: {'SET' if API_KEY else 'NOT SET'}")

if API_KEY:
    genai.configure(api_key=API_KEY)

def call_gemini(prompt, model="models/gemini-2.5-flash"):
    if not API_KEY:
        return f"[MOCKED_RESPONSE] {prompt[:80]}"
    try:
        # Try newer API first
        model_instance = genai.GenerativeModel(model)
        resp = model_instance.generate_content(prompt)
        return resp.text
    except AttributeError:
        # Fallback for older API versions
        try:
            resp = genai.generate_text(prompt=prompt, model=model)
            return resp.result
        except:
            # Final fallback - return mock response for testing
            return f"[MOCKED_RESPONSE] Generated response for: {prompt[:80]}"
    except Exception as e:
        # Return mock response for any other errors (API key issues, rate limits, etc.)
        return f"[MOCKED_RESPONSE] Error: {str(e)[:50]} - Input: {prompt[:50]}"
