from .headers import HeadersScanner
from .technology import TechnologyScanner
from .xss import XssScanner
from .sqli import SqliScanner
from .csrf import CsrfScanner
from .auth import AuthScanner
from .authorization import AuthorizationScanner
from .traversal import TraversalScanner
from .ssrf import SsrfScanner
from .upload import UploadScanner
from .ports import PortsScanner
from .dns import DnsScanner
from .http import HttpScanner

REGISTRY = {
    "headers": HeadersScanner,
    "technology": TechnologyScanner,
    "xss": XssScanner,
    "sqli": SqliScanner,
    "csrf": CsrfScanner,
    "auth": AuthScanner,
    "authorization": AuthorizationScanner,
    "traversal": TraversalScanner,
    "ssrf": SsrfScanner,
    "upload": UploadScanner,
    "ports": PortsScanner,
    "dns": DnsScanner,
    "http": HttpScanner,
}

PROFILES = {
    "Quick": ["headers", "technology"],
    "Standard": ["headers", "technology"],
    "Deep": ["headers", "technology"],
}
