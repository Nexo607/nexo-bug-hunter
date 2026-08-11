from urllib.parse import urlparse,urlunparse
import ipaddress,socket
def normalize(raw):
    raw=raw.strip()
    if not raw.startswith(("http://","https://")): raise ValueError("Target must use HTTP or HTTPS.")
    p=urlparse(raw)
    if not p.hostname or p.username or p.password or p.query or p.fragment: raise ValueError("Enter a clean base URL without credentials, query strings, or fragments.")
    return urlunparse((p.scheme,p.netloc,p.path or "/","","",""))
def public_host(host):
    try:
        a=ipaddress.ip_address(host)
        return not (a.is_private or a.is_loopback or a.is_link_local or a.is_reserved or a.is_multicast or a.is_unspecified)
    except ValueError:
        try:
            ips={x[4][0] for x in socket.getaddrinfo(host,None)}
            return bool(ips) and all(public_host(x) for x in ips)
        except OSError:return False
