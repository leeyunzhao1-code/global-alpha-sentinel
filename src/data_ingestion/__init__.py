"""
Data Ingestion Module

Handles data collection from multiple sources with credibility scoring.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
import logging

logger = logging.getLogger(__name__)


class DataSourceLevel(Enum):
    """Data source credibility levels"""
    A = 0.95
    B = 0.85
    C = 0.60
    D = 0.30


@dataclass
class DataPoint:
    """Single data point with metadata"""
    value: Any
    source: str
    source_level: DataSourceLevel
    timestamp: str
    metric: str

    @property
    def source_weight(self) -> float:
        return self.source_level.value


class DataIngestionEngine:
    """Main data ingestion engine"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.sources = {}
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch(self, metric: str, sources: List[str]) -> List[DataPoint]:
        tasks = []
        for source in sources:
            tasks.append(self._fetch_from_source(metric, source))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        data_points = []
        for result in results:
            if isinstance(result, DataPoint):
                data_points.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Data fetch error: {result}")

        return data_points

    async def _fetch_from_source(self, metric: str, source: str) -> DataPoint:
        return DataPoint(
            value=None,
            source=source,
            source_level=DataSourceLevel.B,
            timestamp="2025-01-01",
            metric=metric
        )

    def calculate_credibility(self, data_points: List[DataPoint]) -> Dict[str, Any]:
        if not data_points:
            return {"value": None, "credibility": 0, "confidence": 0}

        a_level = [dp for dp in data_points if dp.source_level == DataSourceLevel.A]
        b_level = [dp for dp in data_points if dp.source_level == DataSourceLevel.B]

        valid_points = [dp for dp in data_points if dp.value is not None]
        if not valid_points:
            return {"value": None, "credibility": 0, "confidence": 0}

        weighted_sum = sum(dp.value * dp.source_weight for dp in valid_points)
        total_weight = sum(dp.source_weight for dp in valid_points)
        consensus = weighted_sum / total_weight if total_weight > 0 else None

        std_dev = self._calculate_std_dev([dp.value for dp in valid_points])

        if std_dev < 0.01:
            if len(a_level) >= 3:
                credibility = 0.99
            elif len(a_level) >= 2 and len(b_level) >= 1:
                credibility = 0.95
            elif len(a_level) >= 1 and len(b_level) >= 2:
                credibility = 0.90
            elif len(b_level) >= 3:
                credibility = 0.85
            else:
                credibility = max(dp.source_weight for dp in valid_points)
        else:
            conflict_penalty = min(0.3, std_dev * 10)
            base_credibility = max(dp.source_weight for dp in valid_points)
            credibility = max(0.3, base_credibility - conflict_penalty)

        return {
            "value": consensus,
            "credibility": round(credibility, 2),
            "confidence": round(1 - std_dev, 2) if std_dev < 1 else 0,
            "sources": [dp.source for dp in valid_points],
            "std_dev": std_dev
        }

    def _calculate_std_dev(self, values: List[float]) -> float:
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5


class DataSourceRegistry:
    """Registry for data sources"""

    def __init__(self):
        self.sources = {}

    def register(self, name: str, source_config: Dict[str, Any]):
        self.sources[name] = source_config

    def get_source(self, name: str) -> Optional[Dict[str, Any]]:
        return self.sources.get(name)

    def list_sources(self, level: DataSourceLevel = None) -> List[str]:
        if level:
            return [name for name, config in self.sources.items()
                   if config.get("level") == level]
        return list(self.sources.keys())
