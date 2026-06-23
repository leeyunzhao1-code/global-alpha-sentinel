"""
API Module

FastAPI application for the Global Alpha Sentinel system.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from ..agents import (
    CIOAgent, MacroAgent, FinancialAnalystAgent,
    RiskOfficerAgent, ValuationAgent
)

app = FastAPI(
    title="Global Alpha Sentinel API",
    description="Institutional-grade global financial macro warning and value discovery system",
    version="0.1.0"
)


class StockRequest(BaseModel):
    """Stock analysis request"""
    stock_code: str
    market: str
    financial_data: Optional[Dict[str, Any]] = None
    risk_data: Optional[Dict[str, Any]] = None
    valuation_data: Optional[Dict[str, Any]] = None


class MacroRequest(BaseModel):
    """Macro analysis request"""
    country: str
    indicators: Optional[Dict[str, Any]] = None


class AnalysisResponse(BaseModel):
    """Analysis response"""
    stock_code: str
    market: str
    final_score: int
    status: str
    conclusion: str
    details: Dict[str, Any]


# Initialize agents
cio_agent = CIOAgent()
macro_agent = MacroAgent()
financial_agent = FinancialAnalystAgent()
risk_agent = RiskOfficerAgent()
valuation_agent = ValuationAgent()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.1.0"}


@app.post("/analyze/stock", response_model=AnalysisResponse)
async def analyze_stock(request: StockRequest):
    """Analyze a single stock and return investment recommendation"""
    try:
        reports = []

        if request.financial_data:
            financial_report = financial_agent.analyze(
                request.stock_code, request.market, request.financial_data
            )
            reports.append(financial_report)

        if request.risk_data:
            risk_report = risk_agent.analyze(
                request.stock_code, request.market, request.risk_data
            )
            reports.append(risk_report)

        if request.valuation_data:
            valuation_report = valuation_agent.analyze(
                request.stock_code, request.market, request.valuation_data
            )
            reports.append(valuation_report)

        final_report = cio_agent.analyze(
            request.stock_code, request.market, reports
        )

        return AnalysisResponse(
            stock_code=request.stock_code,
            market=request.market,
            final_score=final_report.score,
            status=final_report.status,
            conclusion=final_report.conclusion,
            details=final_report.details
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/macro")
async def analyze_macro(request: MacroRequest):
    """Analyze macroeconomic conditions for a country"""
    try:
        report = macro_agent.analyze(request.country, request.indicators or {})
        return {
            "country": request.country,
            "risk_score": report.score,
            "status": report.status,
            "conclusion": report.conclusion,
            "details": report.details
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/screen/value")
async def value_screen(market: str = "all", limit: int = 100):
    """Screen for undervalued stocks"""
    return {"status": "not_implemented", "market": market, "limit": limit}


@app.get("/screen/risk")
async def risk_screen(market: str = "all", limit: int = 100):
    """Screen for high-risk stocks"""
    return {"status": "not_implemented", "market": market, "limit": limit}


@app.get("/dashboard/macro")
async def macro_dashboard():
    """Get macro dashboard data"""
    return {"status": "not_implemented"}
