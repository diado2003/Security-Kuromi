import whois
from urllib.parse import urlparse


def _normalize_domain(domain_name):
    value = (domain_name or "").strip()
    if not value:
        return ""

    if "://" in value:
        parsed = urlparse(value)
        value = parsed.netloc or parsed.path

    return value.strip("/").lower()

def get_domain_whois(domain_name):
    normalized_domain = _normalize_domain(domain_name)
    if not normalized_domain:
        return {"registered": False, "error": "Domeniu invalid sau gol."}

    try:
        whois_info = whois.whois(normalized_domain)
        if whois_info is None:
            return {
                "registered": False,
                "domain": normalized_domain,
                "error": "WHOIS query returned no data.",
            }

        raw = dict(whois_info)
        registered = bool(whois_info.domain_name)

        if not registered:
            return {
                "registered": False,
                "domain": normalized_domain,
                "raw": raw,
            }

        return {
            "registered": True,
            "domain": normalized_domain,
            "registrar": whois_info.registrar,
            "whois_server": whois_info.whois_server,
            "creation_date": whois_info.creation_date,
            "expiration_date": whois_info.expiration_date,
            "raw": raw,
        }
    except Exception as exc:
        return {
            "registered": False,
            "domain": normalized_domain,
            "error": f"WHOIS query failed: {exc}",
        }


if __name__ == "__main__":
    domain_name = "google.com"
    result = get_domain_whois(domain_name)

    if not result.get("registered"):
        print(f"Domain {domain_name} is not registered.")
        if result.get("error"):
            print(result["error"])
    else:
        print("Domain registrar:", result["registrar"])
        print("WHOIS server:", result["whois_server"])
        print("Domain creation date:", result["creation_date"])
        print("Expiration date:", result["expiration_date"])
        print(result["raw"])
