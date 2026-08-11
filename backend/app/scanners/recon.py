from .base import Scanner
class ReconScanner(Scanner):
    name="recon";description="Safe HTTP metadata, robots and sitemap discovery";category="Reconnaissance"
    async def run(self,target,client):
        out=[];r=await client.get(target,follow_redirects=True)
        out.append({"kind":"http","url":str(r.url),"status":r.status_code,"server":r.headers.get("server"),"powered_by":r.headers.get("x-powered-by"),"content_type":r.headers.get("content-type","")})
        base=str(r.url).rstrip("/")
        for p in ("/robots.txt","/sitemap.xml"):
            x=await client.get(base+p,follow_redirects=False);out.append({"kind":"endpoint","path":p,"status":x.status_code})
        return out
