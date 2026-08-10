from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator

@dataclass
class ScannerContext:
    target: str
    scan_id: int
    request_limit: int
    timeout: float
    emit: object

class BaseScanner(ABC):
    name = "base"
    description = ""
    owasp_category = ""

    def validate_target(self, target: str) -> bool:
        return bool(target)

    @abstractmethod
    async def run(self, ctx: ScannerContext) -> AsyncIterator[dict]:
        if False:
            yield {}

    def parse_results(self, raw: dict) -> dict:
        return raw

    def normalize_finding(self, raw: dict) -> dict:
        return raw
