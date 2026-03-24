# reset_flow_test.py
import requests
import time

BASE_URL = "http://localhost:5000"

def request_reset(email: str):
    r = requests.post(f"{BASE_URL}/forgot-password", json={"email": email}, timeout=10)
    return r.status_code, r.text

def main():
    test_emails = [
        "existing_user@example.com",
        "nonexistent_user@example.com",
    ]

    results = []
    for email in test_emails:
        start = time.time()
        status, body = request_reset(email)
        elapsed = time.time() - start
        results.append((email, status, elapsed, body[:200]))

    for row in results:
        print(row)

if __name__ == "__main__":
    main()