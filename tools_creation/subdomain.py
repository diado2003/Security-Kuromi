import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

REQUEST_TIMEOUT = 5
SLOW_RESPONSE_SECONDS = 2
MAX_WORKERS = 25
BASE_DIR = os.path.dirname(__file__)
DEFAULT_WORDLIST = os.path.join(BASE_DIR, "subdomains-100.txt")
DEFAULT_OUTPUT = os.path.join(BASE_DIR, "discovered_subdomains.txt")

def discover_subdomains(
    domain,
    wordlist_path=DEFAULT_WORDLIST,
    request_timeout=REQUEST_TIMEOUT,
    slow_response_seconds=SLOW_RESPONSE_SECONDS,
    max_candidates=None,
    max_workers=MAX_WORKERS,
):
    discovered_subdomains = []
    events = []
    status_counts = {"discovered": 0, "slow": 0, "timeout": 0, "no_response": 0, "error": 0}

    with open(wordlist_path, encoding="utf-8") as file:
        subdomains = [line.strip() for line in file if line.strip()]
    if max_candidates is not None:
        subdomains = subdomains[: int(max_candidates)]

    def probe_subdomain(subdomain):
        url = f"http://{subdomain}.{domain}"
        try:
            response = requests.get(url, timeout=request_timeout)
            if response.elapsed.total_seconds() > slow_response_seconds:
                return {"status": "slow", "url": url}
        except requests.exceptions.Timeout:
            return {"status": "timeout", "url": url}
        except requests.exceptions.ConnectionError:
            return {"status": "no_response", "url": url}
        except requests.exceptions.RequestException as exc:
            return {"status": "error", "url": url, "message": str(exc)}
        else:
            return {"status": "discovered", "url": url}

    workers = max(1, min(int(max_workers), len(subdomains) if subdomains else 1))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(probe_subdomain, subdomain) for subdomain in subdomains]
        for future in as_completed(futures):
            event = future.result()
            events.append(event)
            status = event["status"]
            status_counts[status] += 1
            if status == "discovered":
                discovered_subdomains.append(event["url"])

    discovered_subdomains.sort()

    return {
        "domain": domain,
        "wordlist_path": wordlist_path,
        "discovered_subdomains": discovered_subdomains,
        "events": events,
        "status_counts": status_counts,
    }


def save_discovered_subdomains(discovered_subdomains, output_path=DEFAULT_OUTPUT):
    with open(output_path, "w", encoding="utf-8") as file:
        for subdomain in discovered_subdomains:
            print(subdomain, file=file)


if __name__ == "__main__":
    domain = "google.com"
    result = discover_subdomains(domain)

    for event in result["events"]:
        status = event["status"]
        if status == "discovered":
            print("[+] Discovered subdomain:", event["url"])
        elif status == "slow":
            print("[-] Slow response from:", event["url"])
        elif status == "timeout":
            print(f"[-] Timeout after {REQUEST_TIMEOUT}s:", event["url"])
        elif status == "no_response":
            print("[-] No response from:", event["url"])
        else:
            print(f"[-] Request failed for {event['url']}: {event.get('message', 'unknown error')}")

    save_discovered_subdomains(result["discovered_subdomains"])


