from .base import BaseScanner, ScannerContext

class SsrfScanner(BaseScanner):
    name = "ssrf"
    description = "Extensible scanner module. No fabricated findings are emitted."
    owasp_category = "OWASP Top 10"

    async def run(self, ctx: ScannerContext):
        await ctx.emit("INFO", "ssrf scanner initialized; no active checks are enabled in the safe baseline.")
        if False:
            yield {}
