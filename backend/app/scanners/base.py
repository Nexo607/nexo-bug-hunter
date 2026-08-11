from dataclasses import dataclass
@dataclass
class FindingResult:
    title:str;severity:str;confidence:int;category:str;url:str;evidence:str;impact:str;remediation:str
    method:str="GET";parameter:str|None=None;cwe:str|None=None
class Scanner:
    name="base";description="";category=""
    async def run(self,target,client): return []
