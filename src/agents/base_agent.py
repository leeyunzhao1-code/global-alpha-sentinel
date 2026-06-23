"""
Base Agent Class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class AgentReport:
    """Standard agent report format"""
    message_id: str
    timestamp: datetime
    from_agent: str
    stock_code: str
    market: str
    report_type: str
    score: int
    status: str
    conclusion: str
    details: Dict[str, Any]
    confidence: float
    data_sources: list
    data_timestamp: datetime


class BaseAgent(ABC):
    """Base class for all agents"""

    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.version = "0.1.0"

    def create_report(self, stock_code: str, market: str, report_type: str,
                      score: int, status: str, conclusion: str,
                      details: Dict[str, Any], confidence: float,
                      data_sources: list) -> AgentReport:
        return AgentReport(
            message_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            from_agent=self.name,
            stock_code=stock_code,
            market=market,
            report_type=report_type,
            score=score,
            status=status,
            conclusion=conclusion,
            details=details,
            confidence=confidence,
            data_sources=data_sources,
            data_timestamp=datetime.utcnow()
        )

    @abstractmethod
    def analyze(self, stock_code: str, market: str, **kwargs) -> AgentReport:
        pass

    def validate_inputs(self, stock_code: str, market: str) -> bool:
        if not stock_code or not market:
            return False
        return True

    def get_status_emoji(self, score: int) -> str:
        if score <= 20:
            return "🟢"
        elif score <= 40:
            return "🟡"
        elif score <= 60:
            return "🟠"
        else:
            return "🔴"

    def __str__(self):
        return f"{self.name} (v{self.version})"
