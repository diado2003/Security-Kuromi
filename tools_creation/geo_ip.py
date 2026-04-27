import ipinfo
import os
import sys
from ipinfo.error import APIError

def get_geo_ip_details(ip_address=None, access_token=None):
    if access_token is None:
        access_token = os.getenv("IPINFO_TOKEN", "").strip()
    if access_token == "<put_your_access_token_here>":
        access_token = ""

    handler = ipinfo.getHandler(access_token or None)
    details = handler.getDetails(ip_address)
    return details.all


if __name__ == "__main__":
    ip_address = input("Enter an IP address to get its geolocation information (or press Enter to use your own IP): ")
    if not ip_address:
        ip_address = None

    try:
        details = get_geo_ip_details(ip_address)
    except APIError as err:
        print(f"ipinfo API error: {err}")
        print("Hint: set a valid token in env var IPINFO_TOKEN.")
        sys.exit(1)

    for key, value in details.items():
        print(f"{key}: {value}")
