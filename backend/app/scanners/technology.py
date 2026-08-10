import httpx
from .base import BaseScanner, ScannerContext

class TechnologyScanner(BaseScanner):
    name = "technology"
    description = "Passive HTTP technology and server-header inventory."
    owasp_category = "Informational"

    async def run(self, ctx: ScannerContext):
        await ctx.emit("INFO", "Technology detection started")
        async with httpx.AsyncClient(follow_redirects=True, timeout=ctx.timeout) as client:
            response = await client.get(ctx.target)
        technologies = []
        if response.headers.get("server"):
            technologies.append("Server: " + response.headers["server"][:200])
        if response.headers.get("x-powered-by"):
            technologies.append("X-Powered-By: " + response.headers["x-powered-by"][:200])
        await ctx.emit("INFO", "Technology detection completed")
        yield {"type": "technology", "target": str(response.url), "technologies": technologies}
