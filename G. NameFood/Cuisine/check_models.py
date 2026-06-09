import os
# pyrefly: ignore [missing-source-for-stubs]
import requests

api_key = None
with open('../.env') as f:
    for line in f:
        if line.startswith('GEMINI_API_KEY='):
            api_key = line.split('=', 1)[1].strip().strip('"').strip("'")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
try:
    response = requests.get(url)
    models = response.json()
    for m in models.get('models', []):
        print(m.get('name'))
except Exception as e:
    print("Error:", e)
