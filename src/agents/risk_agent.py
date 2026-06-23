"""
Risk Officer Agent

Identifies and scores various risks for a company.
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentReport


class RiskOfficerAgent(BaseAgent):
    """Risk identification and scoring agent"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("Risk Officer", config)
        self.risk_categories = [
            "financial_fraud", "delisting", "cashflow", "debt_default",
            "goodwill", "litigation", "regulatory", "management",
            "related_party", "reduction", "pledge"
        ]

    def analyze(self, stock_code: str, market: str,
                risk_data: Dict[str, Any] = None, **kwargs) -> AgentReport:
        risk_data = risk_data or {}
        risks = []
        total_score = 0

        checks = [
            ("financial_fraud", self._detect_fraud_risk),
            ("delisting", self._detect_delisting_risk),
            ("cashflow", self._detect_cashflow_risk),
            ("debt_default", self._detect_debt_risk),
            ("goodwill", self._detect_goodwill_risk),
            ("litigation", self._detect_litigation_risk),
            ("regulatory", self._detect_regulatory_risk),
            ("management", self._detect_management_risk),
            ("related_party", self._detect_related_party_risk),
            ("reduction", self._detect_reduction_risk),
            ("pledge", self._detect_pledge_risk),
        ]

        weights = {
            "financial_fraud": 0.20, "delisting": 0.15, "cashflow": 0.15,
            "debt_default": 0.15, "goodwill": 0.10, "litigation": 0.05,
            "regulatory": 0.10, "management": 0.05, "related_party": 0.05,
            "reduction": 0.05, "pledge": 0.05
        }

        for risk_type, check_func in checks:
            score = check_func(risk_data)
            if score > 50:
                risks.append({
                    "type": risk_type,
                    "score": score,
                    "level": self._get_risk_level(score)
                })
            total_score += score * weights.get(risk_type, 0.05)

        risk_score = min(100, int(total_score))
        status = self._get_status(risk_score)
        conclusion = self._generate_conclusion(risk_score, risks)

        return self.create_report(
            stock_code=stock_code,
            market=market,
            report_type="RISK",
            score=risk_score,
            status=status,
            conclusion=conclusion,
            details={
                "risks": risks,
                "risk_count": len(risks),
                "risk_data": risk_data
            },
            confidence=0.80,
            data_sources=["Exchange", "SEC", "Regulatory", "Court"]
        )

    def _detect_fraud_risk(self, data: Dict) -> int:
        score = 0
        if data.get("ocf_to_net_income", 1) < 0.5:
            score += 30
        if data.get("receivable_growth", 0) > data.get("revenue_growth", 0) * 2:
            score += 20
        if data.get("inventory_growth", 0) > data.get("revenue_growth", 0) * 2:
            score += 15
        if data.get("other_receivables_ratio", 0) > 0.1:
            score += 15
        if data.get("audit_opinion") != "standard":
            score += 20
        return min(100, score)

    def _detect_delisting_risk(self, data: Dict) -> int:
        score = 0
        if data.get("consecutive_losses", 0) >= 2:
            score += 50
        if data.get("stock_price", 1) < 1.0:
            score += 30
        if data.get("net_assets_per_share", 1) < 0:
            score += 20
        return min(100, score)

    def _detect_cashflow_risk(self, data: Dict) -> int:
        score = 0
        if data.get("ocf_negative_years", 0) >= 2:
            score += 40
        if data.get("fcf_negative_years", 0) >= 2:
            score += 30
        if data.get("ocf_to_short_term_debt", 1) < 0.3:
            score += 30
        return min(100, score)

    def _detect_debt_risk(self, data: Dict) -> int:
        score = 0
        if data.get("interest_coverage", 5) < 1:
            score += 50
        elif data.get("interest_coverage", 5) < 1.5:
            score += 30
        if data.get("debt_ratio", 0.5) > 0.7:
            score += 25
        if data.get("short_term_debt_ratio", 0.3) > 0.6:
            score += 15
        if data.get("interest_bearing_debt_to_ebitda", 2) > 5:
            score += 10
        return min(100, score)

    def _detect_goodwill_risk(self, data: Dict) -> int:
        score = 0
        if data.get("goodwill_to_equity", 0) > 0.5:
            score += 50
        elif data.get("goodwill_to_equity", 0) > 0.3:
            score += 30
        if data.get("acquisition_intensity", 0) > 0.3:
            score += 20
        return min(100, score)

    def _detect_litigation_risk(self, data: Dict) -> int:
        score = 0
        if data.get("litigation_amount_to_equity", 0) > 0.1:
            score += 60
        elif data.get("litigation_amount_to_equity", 0) > 0.05:
            score += 30
        if data.get("ongoing_litigations", 0) > 5:
            score += 20
        return min(100, score)

    def _detect_regulatory_risk(self, data: Dict) -> int:
        score = 0
        if data.get("under_investigation", False):
            score += 80
        if data.get("regulatory_penalties_count", 0) > 3:
            score += 30
        elif data.get("regulatory_penalties_count", 0) > 0:
            score += 15
        return min(100, score)

    def _detect_management_risk(self, data: Dict) -> int:
        score = 0
        if data.get("ceo_changes_3y", 0) > 2:
            score += 40
        if data.get("cfo_changes_3y", 0) > 2:
            score += 30
        if data.get("insider_selling", 0) > 0.1:
            score += 30
        return min(100, score)

    def _detect_related_party_risk(self, data: Dict) -> int:
        score = 0
        if data.get("related_party_to_revenue", 0) > 0.3:
            score += 50
        elif data.get("related_party_to_revenue", 0) > 0.15:
            score += 25
        if data.get("related_party_to_cost", 0) > 0.3:
            score += 25
        return min(100, score)

    def _detect_reduction_risk(self, data: Dict) -> int:
        score = 0
        if data.get("major_shareholder_reduction", 0) > 0.05:
            score += 50
        elif data.get("major_shareholder_reduction", 0) > 0.02:
            score += 25
        if data.get("lockup_expiry_6m", False):
            score += 20
        return min(100, score)

    def _detect_pledge_risk(self, data: Dict) -> int:
        score = 0
        if data.get("pledge_ratio", 0) > 0.5:
            score += 60
        elif data.get("pledge_ratio", 0) > 0.3:
            score += 30
        if data.get("pledge_warning_line", False):
            score += 20
        if data.get("pledge_flat_line", False):
            score += 20
        return min(100, score)

    def _get_risk_level(self, score: int) -> str:
        if score >= 80: return "极高"
        elif score >= 60: return "高"
        elif score >= 40: return "中"
        else: return "低"

    def _get_status(self, score: int) -> str:
        if score <= 20: return "SAFE"
        elif score <= 40: return "WATCH"
        elif score <= 60: return "CAUTION"
        else: return "DANGER"

    def _generate_conclusion(self, score: int, risks: List[Dict]) -> str:
        if score >= 80:
            return f"极高风险，发现{len(risks)}项重大风险，建议立即避险"
        elif score >= 60:
            return f"高风险，发现{len(risks)}项风险，建议谨慎"
        elif score >= 40:
            return f"中等风险，发现{len(risks)}项风险，需关注"
        else:
            return f"风险可控，整体安全"
