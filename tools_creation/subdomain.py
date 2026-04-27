import requests

domain = "google.com"
REQUEST_TIMEOUT = 5
SLOW_RESPONSE_SECONDS = 2

# read all subdomains
with open("subdomains-100.txt") as file:
    content = file.read()
    subdomains = content.splitlines()
    discovered_subdomains = []
    for subdomain in subdomains:
        # construct the url
        url = f"http://{subdomain}.{domain}"
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            if response.elapsed.total_seconds() > SLOW_RESPONSE_SECONDS:
                print("[-] Slow response from:", url)
        except requests.exceptions.Timeout:
            print(f"[-] Timeout after {REQUEST_TIMEOUT}s:", url)
            continue
        except requests.exceptions.ConnectionError:
            print("[-] No response from:", url)
            continue
        except requests.exceptions.RequestException as exc:
            print(f"[-] Request failed for {url}: {exc}")
            continue
        else:
            print("[+] Discovered subdomain:", url)
            discovered_subdomains.append(url)

with open("discovered_subdomains.txt", "w") as f:
    for subdomain in discovered_subdomains:
        print(subdomain, file=f)


