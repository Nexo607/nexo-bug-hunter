import httpx
from .base import BaseScanner, ScannerContext

class HeadersScanner(BaseScanner):
    name = "headers"
    description = "Passive HTTP security-header analysis."
    owasp_category = "A05: Security Misconfiguration"

    async def run(self, ctx: ScannerContext):
        await ctx.emit("INFO", "HTTP security-header analysis started")
        async with httpx.AsyncClient(follow_redirects=True, timeout=ctx.timeout) as client:
            response = await client.get(ctx.target)
        headers = {k.lower(): v for k, v in response.headers.items()}
        checks = [
            ("content-security-policy", "Missing Content-Security-Policy", "Medium", "CWE-693"),
            ("strict-transport-security", "Missing Strict-Transport-Security", "Low", "CWE-319"),
            ("x-content-type-options", "Missing X-Content-Type-Options", "Low", "CWE-693"),
            ("referrer-policy", "Missing Referrer-Policy", "Low", "CWE-693"),
        ]
        for key, title, severity, cwe in checks:
            if key not in headers:
                yield {
                    "title": title, "severity": severity, "confidence": "High",
                    "owasp_category": self.owasp_category, "cwe": cwe,
                    "target": ctx.target, "endpoint": str(response.url), "method": "GET",
                    "parameter": "", "evidence": f"Response did not contain the {key} header.",
                    "remediation": f"Configure an appropriate {key} policy for the application."
                }
        await ctx.emit("INFO", "Security-header analysis completed")
