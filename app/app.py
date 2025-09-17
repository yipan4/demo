# app/app.py
# Minimal script that requires 'requests'.
import requests

def fetch_status(url: str) -> int:
    r = requests.get(url, timeout=5)
    return r.status_code

if __name__ == "__main__":
    print(fetch_status("https://example.com"))
