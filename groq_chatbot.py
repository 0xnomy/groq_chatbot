import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Union, Generator

# Load environment variables from .env
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_SYSTEM_PROMPT = "You are Groq API Chatv1, a helpful assistant built at Musketeers Tech. Answer clearly and concisely."
SUPPORTED_MODELS = [
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "gemma2-9b-it",
    "llama-3.1-8b-instant"
]

def generate_response(
    messages: List[Dict],
    model: str,
    stream: bool = False,
    temperature: float = 0.7
) -> Union[str, Generator[str, None, None]]:
    """
    Sends chat history to Groq's OpenAI-compatible API and returns the assistant's response.
    Args:
        messages (list): List of message dicts (role: 'system'|'user'|'assistant', content: str)
        model (str): Model name to use (must be in SUPPORTED_MODELS)
        stream (bool): If True, yields tokens as they arrive. If False, returns full response.
        temperature (float): Sampling temperature for the model.
    Returns:
        str or generator: Assistant's reply or error message, or a generator yielding tokens
    """
    if not GROQ_API_KEY:
        yield "[Error] GROQ_API_KEY not set in .env."
        return
    if not messages or not isinstance(messages, list):
        yield "[Error] No messages provided."
        return
    if model not in SUPPORTED_MODELS:
        yield f"[Error] Unsupported model: {model}"
        return

    # Ensure system prompt is present as first message
    if not messages or messages[0].get("role") != "system":
        messages = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}] + messages

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 1024,
        "top_p": 1.0,
        "stream": stream
    }
    try:
        if stream:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60, stream=True)
            if response.status_code == 429:
                yield "[Rate Limit] Too many requests. Please wait and try again."
                return
            if not response.ok:
                yield f"[API Error] {response.status_code}: {response.text}"
                return
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith('data: '):
                    data = line[6:]
                    if data.strip() == '[DONE]':
                        break
                    try:
                        import json
                        chunk = json.loads(data)
                        delta = chunk["choices"][0]["delta"].get("content", "")
                        if delta:
                            yield delta
                    except Exception:
                        continue
        else:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
            if response.status_code == 429:
                return "[Rate Limit] Too many requests. Please wait and try again."
            if not response.ok:
                return f"[API Error] {response.status_code}: {response.text}"
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        if stream:
            yield "[Timeout] The request to Groq API timed out. Please try again."
        else:
            return "[Timeout] The request to Groq API timed out. Please try again."
    except Exception as e:
        if stream:
            yield f"[Error] {str(e)}"
        else:
            return f"[Error] {str(e)}" 