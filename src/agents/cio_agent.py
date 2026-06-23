"""
CIO Agent (Chief Investment Officer)
"""

from typing import List, Dict, Any
from .base_agent import BaseAgent, AgentReport


class CIOAgent(BaseAgent):
    """Chief Investment Officer - Final decision maker"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("CIO Agent", config)
        self.decision_weights = {
            "risk": 0.40,
            "quality": 0.30,
            "value": 0.30,
        }

    def analyze(self, stock_code: str, market: str,
                reports: List[AgentReport] = None) -> AgentReport:
        if not reports:
            return self.create_report(
                stock_code=stock_code,
                market=market,
                report_type="FINAL_DECISION",
                score=50,
                status="WATCH",
                conclusion="等待各Agent分析报告",
                details={},
                confidence=0.0,
                data_sources=[]
            )

        risk_score = self._get_score(reports, "RISK")
        quality_score = self._get_score(reports, "QUALITY")
        value_score = self._get_score(reports, "VALUATION")

        if risk_score >= 80:
            final_score = 0
            status = "DANGER"
            action = "🔴 卖出"
            reason = f"风险极高({risk_score}/100)，建议立即避险"
        elif risk_score >= 60:
            final_score = 30
            status = "CAUTION"
            action = "🟠 警惕"
            reason = f"风险较高({risk_score}/100)，建议谨慎"
        else:
            composite = (
                quality_score * self.decision_weights["quality"] +
                value_score * self.decision_weights["value"] -
                risk_score * self.decision_weights["risk"]
            )
            final_score = max(0, min(100, int(composite)))

            if final_score >= 70:
                status = "SAFE"
                action = "🟢 买入"
                reason = f"质量好({quality_score})、估值低({value_score})、风险可控({risk_score})"
            elif final_score >= 40:
                status = "WATCH"
                action = "🟡 观察"
                reason = f"条件尚可，建议观察"
            else:
                status = "CAUTION"
                action = "🟠 警惕"
                reason = f"综合评分较低({final_score})"

        return self.create_report(
            stock_code=stock_code,
            market=market,
            report_type="FINAL_DECISION",
            score=final_score,
            status=status,
            conclusion=f"{action} - {reason}",
            details={
                "risk_score": risk_score,
                "quality_score": quality_score,
                "value_score": value_score,
                "composite_score": final_score,
                "action": action,
                "reason": reason,
                "agent_reports": [r.__dict__ for r in reports]
            },
            confidence=0.85,
            data_sources=list(set(sum([r.data_sources for r in reports], [])))
        )

    def _get_score(self, reports: List[AgentReport], report_type: str) -> int:
        for report in reports:
            if report.report_type == report_type:
                return report.score
        return 50
