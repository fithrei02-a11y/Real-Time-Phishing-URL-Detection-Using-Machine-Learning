import requests

url = "http://127.0.0.1:5000/predict"

payload = {
    "url": "https://google.com"
}

for i in range(20):
    try:
        response = requests.post(url, json=payload)
        print(f"Attack Request {i+1}: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")