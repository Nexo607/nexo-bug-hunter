from .passive import PassiveScanner
from .recon import ReconScanner
from .tls import TransportScanner
SCANNERS=[ReconScanner(),TransportScanner(),PassiveScanner()]
CATALOG=[
{"name":"recon","description":"HTTP metadata, robots.txt and sitemap discovery","mode":"passive","status":"implemented"},
{"name":"transport","description":"HTTPS transport review","mode":"passive","status":"implemented"},
{"name":"passive","description":"Headers, cookies and CORS checks","mode":"passive","status":"implemented"},
{"name":"sqli","description":"Bounded candidate analysis; no dumping or destructive verification","mode":"guarded","status":"planned"},
{"name":"xss","description":"Evidence-based XSS candidate analysis","mode":"guarded","status":"planned"},
{"name":"authorization","description":"Authorization review using explicitly supplied test identities","mode":"guarded","status":"planned"},
{"name":"api","description":"API specification and endpoint inventory","mode":"passive","status":"planned"},
]
