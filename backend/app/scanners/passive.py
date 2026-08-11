from .base import Scanner,FindingResult
class PassiveScanner(Scanner):
    name="passive";description="Security headers, cookies, CORS and server disclosure";category="A05 Security Misconfiguration"
    async def run(self,target,client):
        r=await client.get(target,follow_redirects=True); out=[]; hs={k.lower():v for k,v in r.headers.items()}
        for h,sev,fix in [("content-security-policy","Medium","Define a restrictive CSP."),("x-content-type-options","Low","Set X-Content-Type-Options: nosniff."),("referrer-policy","Low","Set an appropriate Referrer-Policy.")]:
            if h not in hs: out.append(FindingResult("Missing "+h.title(),sev,95,self.category,str(r.url),"Header absent in observed response.","Browser-side protections are reduced.",fix))
        if r.url.scheme=="https" and "strict-transport-security" not in hs:
            out.append(FindingResult("Missing HSTS","Medium",95,self.category,str(r.url),"Strict-Transport-Security absent.","HTTPS downgrade protection is reduced.","Configure HSTS after validating HTTPS coverage."))
        for c in r.headers.get_list("set-cookie"):
            if r.url.scheme=="https" and "secure" not in c.lower(): out.append(FindingResult("Cookie missing Secure", "Low",95,self.category,str(r.url),"Observed Set-Cookie without Secure.","Cookie could be sent over insecure transport.","Set Secure on sensitive cookies."))
            if "httponly" not in c.lower(): out.append(FindingResult("Cookie missing HttpOnly","Low",90,self.category,str(r.url),"Observed Set-Cookie without HttpOnly.","Client-side scripts may access the cookie.","Set HttpOnly where appropriate."))
        if hs.get("access-control-allow-origin")=="*": out.append(FindingResult("Wildcard CORS","Medium",90,self.category,str(r.url),"Access-Control-Allow-Origin: *.","Cross-origin exposure may be broader than intended.","Restrict origins to trusted application origins."))
        return out
