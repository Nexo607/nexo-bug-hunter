from .base import BaseScanner, ScannerContext

class PortsScanner(BaseScanner):
    name = "ports"
    description = "Extensible scanner module. No fabricated findings are emitted."
    owasp_category = "OWASP Top 10"

    async def run(self, ctx: ScannerContext):
        await ctx.emit("INFO", "ports scanner initialized; no active checks are enabled in the safe baseline.")
        if False:
            yield {}
