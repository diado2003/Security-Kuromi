import requests
import time
import argparse
import statistics

BASE_URL = "http://127.0.0.1:5000"

def request_reset(username: str):
    r = requests.post(
        f"{BASE_URL}/forgot-password",
        json={"username": username},
        timeout=10
    )
    return r.status_code, r.text

def main():
    global BASE_URL

    parser = argparse.ArgumentParser(description="PoC user enumeration: compare existing/non-existing reset responses.")
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--existing", default="diana")
    parser.add_argument("--missing", default="shrek")
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--expected", choices=["vulnerable", "fixed"], default="fixed")
    args = parser.parse_args()

    BASE_URL = args.base_url.rstrip("/")
    test_usernames = [args.existing, args.missing]

    print("=== User enumeration PoC ===")
    print(f"Target: {BASE_URL}/forgot-password")
    print(f"Expected mode: {args.expected}")
    print("Vulnerable: status/body/timing differs for existing vs missing users.")
    print("Fixed: same status/body shape and similar response time.\n")

    timings = {}

    for username in test_usernames:
        timings[username] = []
        for sample in range(1, args.samples + 1):
            start = time.time()
            status, body = request_reset(username)
            elapsed = time.time() - start
            timings[username].append(elapsed)
            print(f"[{username} sample {sample}] status={status} time={elapsed:.4f}s body={body}")

    existing_avg = statistics.mean(timings[args.existing])
    missing_avg = statistics.mean(timings[args.missing])
    delta = abs(existing_avg - missing_avg)

    print("\n=== Result ===")
    print(f"Average existing={existing_avg:.4f}s missing={missing_avg:.4f}s delta={delta:.4f}s")
    if args.expected == "fixed":
        print("PASS" if delta < 0.15 else "CHECK MANUALLY: fixed timing should be close.")
    else:
        print("PASS" if delta >= 0.15 else "CHECK MANUALLY: vulnerable mode should reveal a difference.")

if __name__ == "__main__":
    main()
