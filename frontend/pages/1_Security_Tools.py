import os
import sys
import streamlit as st
import requests

# Ensure imports work when page runs from the frontend folder.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tools_creation.fast_port import scan_open_ports
from tools_creation.geo_ip import get_geo_ip_details
from tools_creation.domain_whois import get_domain_whois
from tools_creation.subdomain import discover_subdomains, save_discovered_subdomains

KUROMI_IMAGE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kuromi.png"))
if os.path.exists(KUROMI_IMAGE):
    st.sidebar.image(KUROMI_IMAGE, use_container_width=True)
    st.sidebar.markdown("Give me an IP/domain, and I will expose every weak spot.")


st.title("Security Tools")
st.caption("Fast Port Scan, Geo IP lookup și Domain WHOIS într-o singură pagină.")
st.info("FETCH ME THEIR IP/DOMAIN. I will reveal what it tries to hide.")

st.markdown("---")

st.subheader("1) Fast Port Scanner")
with st.form("fast_port_form"):
    host = st.text_input("Host / IP", value="127.0.0.1")
    col1, col2 = st.columns(2)
    with col1:
        start_port = st.number_input("Start port", min_value=1, max_value=65535, value=75, step=1)
    with col2:
        end_port = st.number_input("End port", min_value=1, max_value=65535, value=85, step=1)
    run_scan = st.form_submit_button("Scan ports")

if run_scan:
    if not host.strip():
        st.error("Completează host-ul.")
    else:
        with st.spinner("Scanning ports..."):
            try:
                open_ports = scan_open_ports(host.strip(), int(start_port), int(end_port))
                st.success(f"Scan finalizat pentru {host}.")
                if open_ports:
                    st.write("Porturi deschise:")
                    st.code(", ".join(str(p) for p in open_ports), language="text")
                else:
                    st.info("Nu au fost găsite porturi deschise în intervalul ales.")
            except Exception as exc:
                st.error(f"Eroare la scanare: {exc}")

st.markdown("---")

st.subheader("2) Geo IP")
with st.form("geo_ip_form"):
    geo_ip = st.text_input("IP pentru geolocație (lasă gol pentru IP-ul tău public)", value="")
    token = st.text_input("IPInfo token (opțional)", type="password", value="")
    run_geo = st.form_submit_button("Get Geo IP")

if run_geo:
    with st.spinner("Fetching geolocation..."):
        try:
            details = get_geo_ip_details(geo_ip.strip() or None, token.strip() or None)
            st.success("Date geolocație obținute.")
            st.json(details)
        except requests.RequestException as exc:
            st.error(f"Eroare de rețea: {exc}")
        except Exception as exc:
            st.error(f"Eroare Geo IP: {exc}")

st.markdown("---")

st.subheader("3) Domain WHOIS")
with st.form("whois_form"):
    domain_name = st.text_input("Domain", value="google.com")
    run_whois = st.form_submit_button("Check WHOIS")

if run_whois:
    if not domain_name.strip():
        st.error("Completează domeniul.")
    else:
        with st.spinner("Querying WHOIS..."):
            try:
                result = get_domain_whois(domain_name.strip())
                if result is None:
                    result = {
                        "registered": False,
                        "error": "WHOIS did not return any data.",
                    }
                elif not isinstance(result, dict):
                    result = {
                        "registered": False,
                        "error": f"WHOIS returned an invalid response type: {type(result).__name__}",
                    }
                if not result.get("registered"):
                    if result.get("error"):
                        st.error(result.get("error"))
                    else:
                        st.warning("Domeniul nu pare înregistrat.")
                else:
                    st.success("WHOIS găsit.")
                    st.write(f"Domain: {result.get('domain')}")
                    st.write(f"Registrar: {result.get('registrar')}")
                    st.write(f"WHOIS server: {result.get('whois_server')}")
                    st.write(f"Creation date: {result.get('creation_date')}")
                    st.write(f"Expiration date: {result.get('expiration_date')}")
                    with st.expander("Raw WHOIS"):
                        st.json(result.get("raw", {}))
            except Exception as exc:
                st.error(f"Eroare WHOIS: {exc}")

st.markdown("---")

st.subheader("4) Subdomain Discovery")
with st.form("subdomain_form"):
    target_domain = st.text_input("Target domain", value="google.com")
    col1, col2, col3 = st.columns(3)
    with col1:
        request_timeout = st.number_input("Request timeout (sec)", min_value=1, max_value=15, value=3, step=1)
    with col2:
        max_candidates = st.number_input("Max subdomains from wordlist", min_value=10, max_value=1000, value=100, step=10)
    with col3:
        max_workers = st.number_input("Workers", min_value=1, max_value=100, value=25, step=1)
    save_results = st.checkbox("Salvează și în discovered_subdomains.txt", value=True)
    run_subdomain = st.form_submit_button("Discover subdomains")

if run_subdomain:
    if not target_domain.strip():
        st.error("Completează domeniul țintă.")
    else:
        with st.spinner("Discovering subdomains..."):
            try:
                result = discover_subdomains(
                    target_domain.strip().lower(),
                    request_timeout=int(request_timeout),
                    max_candidates=int(max_candidates),
                    max_workers=int(max_workers),
                )
                discovered = result.get("discovered_subdomains", [])
                status_counts = result.get("status_counts", {})

                st.caption(
                    f"Summary: discovered={status_counts.get('discovered', 0)}, "
                    f"no_response={status_counts.get('no_response', 0)}, "
                    f"timeout={status_counts.get('timeout', 0)}, "
                    f"errors={status_counts.get('error', 0)}"
                )

                if discovered:
                    st.success(f"Găsite {len(discovered)} subdomenii.")
                    st.code("\n".join(discovered), language="text")
                    if save_results:
                        save_discovered_subdomains(discovered)
                        st.caption("Rezultatele au fost salvate în discovered_subdomains.txt")
                else:
                    st.warning("Nu au fost descoperite subdomenii pentru domeniul introdus.")

                with st.expander("Event log"):
                    st.json(result.get("events", []))
            except Exception as exc:
                st.error(f"Eroare la subdomain discovery: {exc}")
