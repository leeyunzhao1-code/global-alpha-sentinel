"""
Valuation Agent

Calculates fair value and identifies undervalued opportunities.
"""

from typing import Dict, Any
import numpy as np
from .base_agent import BaseAgent, AgentReport


class ValuationAgent(BaseAgent):
    """Valuation analysis agent"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("Valuation Analyst", config)

    def analyze(self, stock_code: str, market: str,
                valuation_data: Dict[str, Any] = None, **kwargs) -> AgentReport:
        valuation_data = valuation_data or {}

        passes_screen = self._value_screen(valuation_data)

        if passes_screen:
            value_score = self._calculate_value_score(valuation_data)
        else:
            value_score = 0

        fair_value = self._calculate_fair_value(valuation_data)
        current_price = valuation_data.get("current_price", 0)
        undervaluation = (fair_value - current_price) / current_price if current_price > 0 else 0

        status = self._get_value_status(value_score, undervaluation)
        conclusion = self._generate_conclusion(value_score, undervaluation, passes_screen)

        return self.create_report(
            stock_code=stock_code,
            market=market,
            report_type="VALUATION",
            score=value_score,
            status=status,
            conclusion=conclusion,
            details={
                "fair_value": fair_value,
                "current_price": current_price,
                "undervaluation": undervaluation,
                "passes_screen": passes_screen,
                "valuation_data": valuation_data
            },
            confidence=0.75,
            data_sources=["FactSet", "Morningstar", "Exchange"]
        )

    def _value_screen(self, data: Dict) -> bool:
        if data.get("roe", 0) < data.get("industry_avg_roe", 10) * 0.5:
            return False
        if data.get("debt_ratio", 0.5) > 0.7:
            return False
        if data.get("fcf_growth_5y", 0) < 0:
            return False
        if data.get("revenue_growth_3y", 0) < 0:
            return False
        if data.get("profit_margin", 0) < 0:
            return False

        criteria_met = 0
        if data.get("pe", 20) < data.get("industry_avg_pe", 20) * 0.7:
            criteria_met += 1
        if data.get("pb", 2) < data.get("industry_avg_pb", 2) * 0.7:
            criteria_met += 1
        if data.get("ps", 3) < data.get("industry_avg_ps", 3) * 0.7:
            criteria_met += 1
        if data.get("ev_ebitda", 12) < data.get("industry_avg_ev_ebitda", 12) * 0.7:
            criteria_met += 1
        if data.get("fcf_yield", 0) > 0.05:
            criteria_met += 1
        if data.get("dividend_yield", 0) > 0.03:
            criteria_met += 1
        if data.get("peg", 1) < 1.0:
            criteria_met += 1

        if criteria_met < 2:
            return False

        if data.get("roe", 0) < data.get("industry_avg_roe", 10):
            return False
        if not data.get("fcf_positive_5y", True):
            return False
        if data.get("debt_ratio", 0.5) > 0.6:
            return False

        return True

    def _calculate_value_score(self, data: Dict) -> int:
        scores = []

        pe_percentile = data.get("pe_percentile", 50)
        if pe_percentile < 10: scores.append(95)
        elif pe_percentile < 20: scores.append(85)
        elif pe_percentile < 30: scores.append(75)
        elif pe_percentile < 40: scores.append(65)
        else: scores.append(50)

        pb_percentile = data.get("pb_percentile", 50)
        if pb_percentile < 10: scores.append(95)
        elif pb_percentile < 20: scores.append(85)
        elif pb_percentile < 30: scores.append(75)
        elif pb_percentile < 40: scores.append(65)
        else: scores.append(50)

        fcf_yield = data.get("fcf_yield", 0.03)
        if fcf_yield > 0.08: scores.append(100)
        elif fcf_yield > 0.06: scores.append(90)
        elif fcf_yield > 0.05: scores.append(80)
        elif fcf_yield > 0.04: scores.append(70)
        elif fcf_yield > 0.03: scores.append(60)
        else: scores.append(50)

        peg = data.get("peg", 1.5)
        if peg < 0.5: scores.append(100)
        elif peg < 0.8: scores.append(90)
        elif peg < 1.0: scores.append(80)
        elif peg < 1.2: scores.append(65)
        elif peg < 1.5: scores.append(50)
        else: scores.append(30)

        dcf_discount = data.get("dcf_discount", 0)
        if dcf_discount > 0.5: scores.append(100)
        elif dcf_discount > 0.3: scores.append(90)
        elif dcf_discount > 0.2: scores.append(80)
        elif dcf_discount > 0.1: scores.append(65)
        else: scores.append(50)

        div_yield = data.get("dividend_yield", 0.01)
        if div_yield > 0.05: scores.append(100)
        elif div_yield > 0.04: scores.append(90)
        elif div_yield > 0.03: scores.append(80)
        elif div_yield > 0.025: scores.append(70)
        elif div_yield > 0.02: scores.append(60)
        else: scores.append(50)

        return int(np.mean(scores)) if scores else 50

    def _calculate_fair_value(self, data: Dict) -> float:
        current_price = data.get("current_price", 0)
        dcf_value = data.get("dcf_fair_value", 0)

        peers = data.get("peers", [])
        if peers:
            avg_pe = np.mean([p.get("pe", 20) for p in peers])
            avg_pb = np.mean([p.get("pb", 2) for p in peers])
            eps = data.get("eps", 0)
            bps = data.get("bps", 0)
            comp_pe_value = eps * avg_pe
            comp_pb_value = bps * avg_pb
        else:
            comp_pe_value = 0
            comp_pb_value = 0

        historical_pe = data.get("historical_pe", 20)
        eps = data.get("eps", 0)
        hist_value = eps * historical_pe

        values = [v for v in [dcf_value, comp_pe_value, comp_pb_value, hist_value] if v > 0]
        if values:
            return float(np.median(values))
        return current_price

    def _get_value_status(self, score: int, undervaluation: float) -> str:
        if score >= 80 and undervaluation > 0.3:
            return "SAFE"
        elif score >= 60 and undervaluation > 0.1:
            return "WATCH"
        elif score >= 40:
            return "CAUTION"
        else:
            return "DANGER"

    def _generate_conclusion(self, score: int, undervaluation: float,
                             passes_screen: bool) -> str:
        if not passes_screen:
            return "未通过价值筛选，可能为价值陷阱"
        if score >= 80 and undervaluation > 0.3:
            return f"估值极低，低估{undervaluation:.1%}，具备显著投资价值"
        elif score >= 60 and undervaluation > 0.1:
            return f"估值偏低，低估{undervaluation:.1%}，值得关注"
        elif score >= 40:
            return "估值合理，处于合理价值区间"
        else:
            return "估值偏高，可能高估"
