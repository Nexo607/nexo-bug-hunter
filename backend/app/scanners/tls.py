from .base import Scanner,FindingResult
class TransportScanner(Scanner):
    name="transport";description="Passive HTTPS transport checks";category="A02 Cryptographic Failures"
    async def run(self,target,client):
        if target.startswith("http://"):
            return [FindingResult("Target uses HTTP","Medium",100,self.category,target,"Assessment target uses cleartext HTTP.","Traffic may be exposed to network interception.","Use HTTPS and redirect HTTP to HTTPS.")]
        return []
