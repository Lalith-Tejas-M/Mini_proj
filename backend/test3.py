import requests
import json

url = "http://127.0.0.1:8000/api/insights/generate"
payload = {
    "topic": "We repaired things instead of buying new ones.",
    "user_id": "e6c89e85-da3d-44f1-8b5a-b857c5780af7"
}
try:
    res = requests.post(url, json=payload)
    with open("test_output.json", "w") as f:
        f.write(res.text)
except Exception as e:
    print(e)
