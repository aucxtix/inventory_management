import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
try:
    r = requests.get(url)
    models = r.json()
    for m in models.get('models', []):
        if 'gemini' in m['name']:
            print(m['name'])
except Exception as e:
    print(e)
