import requests
import time
import argparse

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
    global BASE_URL

    parser = argparse.ArgumentParser(description="PoC brute force: vulnerable allows many tries; fixed locks/rate-limits.")
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--username", default="diana")
    parser.add_argument("--expected", choices=["vulnerable", "fixed"], default="fixed")
    args = parser.parse_args()

    BASE_URL = args.base_url.rstrip("/")
    target_username = args.username
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

    print("=== Brute force PoC ===")
    print(f"Target: {BASE_URL}/login")
    print(f"Expected mode: {args.expected}")
    print("Vulnerable: unlimited attempts may eventually find a password.")
    print("Fixed: repeated failures should return generic errors and then 429 lockout.\n")

    lockout_seen = False
    success_seen = False

    for pwd in common_passwords:
        print(f"POST /login username={target_username!r} password={pwd!r}")
        status, body = login(target_username, pwd)
        print(f"Status: {status}, Response: {body}")

        if status == 429:
            print("Lockout triggered: too many failed login attempts.")
            lockout_seen = True
            break

        if status == 200 and isinstance(body, dict) and body.get("success") is True:
            print(f"Success! Found password: {pwd}")
            success_seen = True
            break
        time.sleep(1)  

    print("\n=== Result ===")
    if args.expected == "fixed":
        print("PASS" if lockout_seen and not success_seen else "CHECK MANUALLY: fixed mode should lock before password discovery.")
    else:
        print("PASS" if success_seen or not lockout_seen else "CHECK MANUALLY: vulnerable mode should not lock/rate-limit.")

if __name__ == "__main__":
    main()
