import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def request_reset(username: str):
    r = requests.post(
        f"{BASE_URL}/forgot-password",
        json={"username": username},
        timeout=10
    )
    return r.status_code, r.text

def main():
    test_usernames = ["diana", "shrek"]

    for username in test_usernames:
        start = time.time()
        status, body = request_reset(username)
        elapsed = time.time() - start
        print((username, status, elapsed, body))

if __name__ == "__main__":
    main()