"""
Financial Analyst Agent

Analyzes company financial statements and calculates quality scores.
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentReport


class FinancialAnalystAgent(BaseAgent):
    """Financial analysis agent"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("Financial Analyst", config)
        self.scoring_weights = {
            "profitability": 0.20,
            "growth": 0.20,
            "cashflow": 0.20,
            "efficiency": 0.15,
            "health": 0.15,
            "shareholder": 0.10
        }

    def analyze(self, stock_code: str, market: str,
                financial_data: Dict[str, Any] = None, **kwargs) -> AgentReport:
        financial_data = financial_data or {}

        profitability = self._score_profitability(financial_data)
        growth = self._score_growth(financial_data)
        cashflow = self._score_cashflow(financial_data)
        efficiency = self._score_efficiency(financial_data)
        health = self._score_health(financial_data)
        shareholder = self._score_shareholder(financial_data)

        quality_score = int(
            profitability * self.scoring_weights["profitability"] +
            growth * self.scoring_weights["growth"] +
            cashflow * self.scoring_weights["cashflow"] +
            efficiency * self.scoring_weights["efficiency"] +
            health * self.scoring_weights["health"] +
            shareholder * self.scoring_weights["shareholder"]
        )

        status = self._get_status(quality_score)
        conclusion = self._generate_conclusion(
            quality_score, profitability, growth, cashflow
        )

        return self.create_report(
            stock_code=stock_code,
            market=market,
            report_type="QUALITY",
            score=quality_score,
            status=status,
            conclusion=conclusion,
            details={
                "profitability_score": profitability,
                "growth_score": growth,
                "cashflow_score": cashflow,
                "efficiency_score": efficiency,
                "health_score": health,
                "shareholder_score": shareholder,
                "financial_data": financial_data
            },
            confidence=0.85,
            data_sources=["Exchange", "FactSet", "Morningstar"]
        )

    def _score_profitability(self, data: Dict) -> int:
        score = 0
        roe = data.get("roe", 0)
        if roe > 20: score += 30
        elif roe > 15: score += 24
        elif roe > 10: score += 18
        elif roe > 5: score += 12
        else: score += 6

        roa = data.get("roa", 0)
        if roa > 10: score += 20
        elif roa > 7: score += 16
        elif roa > 5: score += 12
        elif roa > 3: score += 8
        else: score += 4

        roic = data.get("roic", 0)
        if roic > 15: score += 20
        elif roic > 12: score += 16
        elif roic > 8: score += 12
        elif roic > 5: score += 8
        else: score += 4

        gross_margin = data.get("gross_margin", 0)
        if gross_margin > 40: score += 15
        elif gross_margin > 30: score += 12
        elif gross_margin > 20: score += 9
        elif gross_margin > 15: score += 6
        else: score += 3

        net_margin = data.get("net_margin", 0)
        if net_margin > 20: score += 15
        elif net_margin > 15: score += 12
        elif net_margin > 10: score += 9
        elif net_margin > 5: score += 6
        else: score += 3

        return min(100, score)

    def _score_growth(self, data: Dict) -> int:
        score = 0
        revenue_growth = data.get("revenue_growth_3y", 0)
        if revenue_growth > 20: score += 35
        elif revenue_growth > 15: score += 28
        elif revenue_growth > 10: score += 21
        elif revenue_growth > 5: score += 14
        else: score += 7

        profit_growth = data.get("profit_growth_3y", 0)
        if profit_growth > 25: score += 35
        elif profit_growth > 18: score += 28
        elif profit_growth > 12: score += 21
        elif profit_growth > 5: score += 14
        else: score += 7

        fcf_growth = data.get("fcf_growth_3y", 0)
        if fcf_growth > 20: score += 30
        elif fcf_growth > 15: score += 24
        elif fcf_growth > 10: score += 18
        elif fcf_growth > 5: score += 12
        else: score += 6

        return min(100, score)

    def _score_cashflow(self, data: Dict) -> int:
        score = 0
        ocf_ratio = data.get("ocf_to_net_income", 0)
        if ocf_ratio > 1.2: score += 30
        elif ocf_ratio > 1.0: score += 24
        elif ocf_ratio > 0.8: score += 18
        elif ocf_ratio > 0.5: score += 12
        else: score += 6

        fcf_ratio = data.get("fcf_to_net_income", 0)
        if fcf_ratio > 0.8: score += 30
        elif fcf_ratio > 0.6: score += 24
        elif fcf_ratio > 0.4: score += 18
        elif fcf_ratio > 0.2: score += 12
        else: score += 6

        if data.get("ocf_positive_5y", False):
            score += 20
        if data.get("fcf_positive_5y", False):
            score += 20

        return min(100, score)

    def _score_efficiency(self, data: Dict) -> int:
        score = 0
        asset_turnover = data.get("asset_turnover", 0)
        if asset_turnover > 1.0: score += 30
        elif asset_turnover > 0.8: score += 24
        elif asset_turnover > 0.6: score += 18
        elif asset_turnover > 0.4: score += 12
        else: score += 6

        inventory_days = data.get("inventory_turnover_days", 100)
        if inventory_days < 30: score += 20
        elif inventory_days < 60: score += 16
        elif inventory_days < 90: score += 12
        elif inventory_days < 120: score += 8
        else: score += 4

        receivable_days = data.get("receivable_turnover_days", 60)
        if receivable_days < 30: score += 20
        elif receivable_days < 45: score += 16
        elif receivable_days < 60: score += 12
        elif receivable_days < 90: score += 8
        else: score += 4

        if data.get("fixed_asset_turnover", 0) > 3: score += 15
        elif data.get("fixed_asset_turnover", 0) > 2: score += 12
        elif data.get("fixed_asset_turnover", 0) > 1: score += 9
        else: score += 6

        capex_to_depreciation = data.get("capex_to_depreciation", 1.5)
        if 1.0 <= capex_to_depreciation <= 2.0: score += 15
        elif capex_to_depreciation < 3.0: score += 12
        else: score += 6

        return min(100, score)

    def _score_health(self, data: Dict) -> int:
        score = 0
        debt_ratio = data.get("debt_ratio", 0.5)
        if debt_ratio < 0.4: score += 25
        elif debt_ratio < 0.5: score += 20
        elif debt_ratio < 0.6: score += 15
        elif debt_ratio < 0.7: score += 10
        else: score += 5

        interest_coverage = data.get("interest_coverage", 5)
        if interest_coverage > 10: score += 25
        elif interest_coverage > 5: score += 20
        elif interest_coverage > 3: score += 15
        elif interest_coverage > 1.5: score += 10
        else: score += 5

        current_ratio = data.get("current_ratio", 1.5)
        if current_ratio > 2.0: score += 20
        elif current_ratio > 1.5: score += 16
        elif current_ratio > 1.2: score += 12
        elif current_ratio > 1.0: score += 8
        else: score += 4

        quick_ratio = data.get("quick_ratio", 1.2)
        if quick_ratio > 1.5: score += 15
        elif quick_ratio > 1.2: score += 12
        elif quick_ratio > 1.0: score += 9
        elif quick_ratio > 0.8: score += 6
        else: score += 3

        debt_to_ebitda = data.get("interest_bearing_debt_to_ebitda", 2.0)
        if debt_to_ebitda < 1.0: score += 15
        elif debt_to_ebitda < 2.0: score += 12
        elif debt_to_ebitda < 3.0: score += 9
        elif debt_to_ebitda < 4.0: score += 6
        else: score += 3

        return min(100, score)

    def _score_shareholder(self, data: Dict) -> int:
        score = 0
        payout_ratio = data.get("payout_ratio", 0.3)
        if payout_ratio > 0.4: score += 30
        elif payout_ratio > 0.3: score += 24
        elif payout_ratio > 0.2: score += 18
        elif payout_ratio > 0.1: score += 12
        else: score += 6

        dividend_yield = data.get("dividend_yield", 0.02)
        if dividend_yield > 0.03: score += 30
        elif dividend_yield > 0.02: score += 24
        elif dividend_yield > 0.015: score += 18
        elif dividend_yield > 0.01: score += 12
        else: score += 6

        if data.get("buyback", False):
            score += 20

        equity_growth = data.get("equity_growth_3y", 0.1)
        if equity_growth > 0.15: score += 20
        elif equity_growth > 0.10: score += 16
        elif equity_growth > 0.05: score += 12
        else: score += 8

        return min(100, score)

    def _get_status(self, score: int) -> str:
        if score >= 80: return "SAFE"
        elif score >= 60: return "WATCH"
        elif score >= 40: return "CAUTION"
        else: return "DANGER"

    def _generate_conclusion(self, total: int, profitability: int,
                             growth: int, cashflow: int) -> str:
        if total >= 80:
            return f"财务质量优秀，盈利({profitability})、成长({growth})、现金流({cashflow})均表现强劲"
        elif total >= 60:
            return f"财务质量良好，主要指标表现稳健"
        elif total >= 40:
            return f"财务质量一般，部分指标需关注"
        else:
            return f"财务质量较差，存在较多财务隐患"
