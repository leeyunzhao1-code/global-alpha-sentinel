"""
Macro Research Agent

Monitors global macroeconomic indicators and calculates country/region risk scores.
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentReport


class MacroAgent(BaseAgent):
    """Macroeconomic research agent"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("Macro Agent", config)
        self.indicators = [
            "gdp", "cpi", "core_cpi", "ppi", "pmi", "ism",
            "unemployment", "m0", "m1", "m2", "interest_rate",
            "yield_curve", "credit_spread", "liquidity_index"
        ]

    def analyze(self, country: str, indicators: Dict[str, Any] = None,
                **kwargs) -> AgentReport:
        indicators = indicators or {}

        recession_prob = self._calculate_recession_probability(indicators)
        liquidity_risk = self._calculate_liquidity_risk(indicators)
        inflation_risk = self._calculate_inflation_risk(indicators)
        yield_curve_risk = self._calculate_yield_curve_risk(indicators)

        risk_score = int(
            recession_prob * 0.35 +
            liquidity_risk * 0.25 +
            inflation_risk * 0.20 +
            yield_curve_risk * 0.20
        )

        status = self._get_status(risk_score)
        conclusion = self._generate_conclusion(risk_score, indicators)

        return self.create_report(
            stock_code=country,
            market="GLOBAL",
            report_type="MACRO",
            score=risk_score,
            status=status,
            conclusion=conclusion,
            details={
                "recession_probability": recession_prob,
                "liquidity_risk": liquidity_risk,
                "inflation_risk": inflation_risk,
                "yield_curve_risk": yield_curve_risk,
                "indicators": indicators
            },
            confidence=0.80,
            data_sources=["BLS", "Fed", "Treasury", "IMF"]
        )

    def _calculate_recession_probability(self, indicators: Dict) -> int:
        score = 0
        if indicators.get("yield_curve_10y_2y", 0) < 0:
            score += 40
        elif indicators.get("yield_curve_10y_2y", 0) < 0.5:
            score += 20

        if indicators.get("unemployment_change", 0) > 0.5:
            score += 25
        elif indicators.get("unemployment_change", 0) > 0.2:
            score += 15

        if indicators.get("pmi", 50) < 45:
            score += 20
        elif indicators.get("pmi", 50) < 50:
            score += 10

        if indicators.get("gdp_growth", 0) < 0:
            score += 15
        elif indicators.get("gdp_growth", 0) < 1:
            score += 5

        return min(100, score)

    def _calculate_liquidity_risk(self, indicators: Dict) -> int:
        score = 0
        if indicators.get("central_bank_bs_change", 0) < -5:
            score += 40
        elif indicators.get("central_bank_bs_change", 0) < -2:
            score += 20

        if indicators.get("sofr_volatility", 0) > 50:
            score += 30

        if indicators.get("credit_spread", 0) > 500:
            score += 30
        elif indicators.get("credit_spread", 0) > 300:
            score += 15

        return min(100, score)

    def _calculate_inflation_risk(self, indicators: Dict) -> int:
        score = 0
        cpi = indicators.get("cpi", 2.0)
        if cpi > 6:
            score += 40
        elif cpi > 4:
            score += 25
        elif cpi > 3:
            score += 15

        if indicators.get("cpi_change", 0) > 1.0:
            score += 20

        return min(100, score)

    def _calculate_yield_curve_risk(self, indicators: Dict) -> int:
        spread = indicators.get("yield_curve_10y_2y", 1.0)
        if spread < -0.5:
            return 80
        elif spread < 0:
            return 60
        elif spread < 0.5:
            return 40
        elif spread < 1.0:
            return 20
        else:
            return 0

    def _get_status(self, score: int) -> str:
        if score <= 30:
            return "SAFE"
        elif score <= 50:
            return "WATCH"
        elif score <= 70:
            return "CAUTION"
        else:
            return "DANGER"

    def _generate_conclusion(self, score: int, indicators: Dict) -> str:
        if score >= 80:
            return "宏观经济处于极高风险状态，建议大幅降低仓位"
        elif score >= 60:
            return "宏观经济风险较高，建议谨慎配置"
        elif score >= 40:
            return "宏观经济存在中等风险，保持关注"
        elif score >= 20:
            return "宏观经济基本稳定，适度关注"
        else:
            return "宏观经济环境良好"
