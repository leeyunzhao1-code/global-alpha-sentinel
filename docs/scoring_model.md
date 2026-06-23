# 评分模型详解

## 1. 企业质量评分（Quality Score）

### 1.1 评分公式

```
Quality Score = Σ(维度得分 × 维度权重)

维度：
- 盈利能力 (20%)
- 成长能力 (20%)
- 现金流质量 (20%)
- 资本效率 (15%)
- 财务健康度 (15%)
- 股东回报 (10%)
```

### 1.2 评分示例

```python
# 假设公司A的财务数据
company_a = {
    "roe": 22.0,          # ROE 22%
    "roa": 12.0,          # ROA 12%
    "roic": 18.0,         # ROIC 18%
    "gross_margin": 45.0, # 毛利率 45%
    "net_margin": 22.0,   # 净利率 22%
    "revenue_growth_3y": 18.0,   # 营收3年CAGR 18%
    "profit_growth_3y": 25.0,    # 利润3年CAGR 25%
    "fcf_growth_3y": 20.0,       # FCF 3年CAGR 20%
    "ocf_to_net_income": 1.3,    # 经营现金流/净利润 1.3
    "fcf_to_net_income": 0.9,    # FCF/净利润 0.9
    "debt_ratio": 35.0,          # 资产负债率 35%
    "interest_coverage": 15.0,   # 利息覆盖 15倍
}

# 评分计算
quality_score = QualityScoreCalculator(company_a)
quality_score.calculate()

# 输出
# Quality Score: 88/100 (A级)
# 状态: 🟢 优秀
# 优势: ROE极高、现金流健康、成长性强
# 劣势: 无明显劣势
```

## 2. 低估值评分（Value Score）

### 2.1 筛选逻辑

```python
class ValueDiscoveryEngine:
    """低估值发现引擎"""
    
    def screen(self, stock: Stock) -> ValueScreenResult:
        # 第一步：排除价值陷阱
        if not self._pass_exclusion_checks(stock):
            return ValueScreenResult(passed=False, reason="未通过排除条件")
        
        # 第二步：检查估值条件（至少满足2项）
        valuation_met = self._check_valuation_criteria(stock)
        if valuation_met.count(True) < 2:
            return ValueScreenResult(passed=False, reason="估值条件不足")
        
        # 第三步：检查质量条件（必须全部满足）
        quality_met = self._check_quality_criteria(stock)
        if not all(quality_met):
            return ValueScreenResult(passed=False, reason="质量条件不足")
        
        # 第四步：计算价值评分
        value_score = self._calculate_value_score(stock)
        
        return ValueScreenResult(
            passed=True,
            value_score=value_score,
            fair_value=self._calculate_fair_value(stock),
            undervaluation=self._calculate_undervaluation(stock)
        )
```

### 2.2 估值方法

```python
class ValuationMethods:
    """多种估值方法"""
    
    @staticmethod
    def dcf_valuation(stock: Stock) -> float:
        """DCF估值"""
        # 预测未来10年FCF
        fcf_projections = project_fcf(stock, years=10)
        
        # 计算WACC
        wacc = calculate_wacc(stock)
        
        # 终值
        terminal_value = fcf_projections[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
        
        # 现值
        pv_fcf = sum([fcf / (1 + wacc) ** i for i, fcf in enumerate(fcf_projections)])
        pv_terminal = terminal_value / (1 + wacc) ** 10
        
        return pv_fcf + pv_terminal - stock.net_debt
    
    @staticmethod
    def comparable_valuation(stock: Stock) -> float:
        """可比公司估值"""
        peers = get_industry_peers(stock.industry)
        
        # 计算行业平均估值倍数
        avg_pe = np.mean([p.pe for p in peers])
        avg_pb = np.mean([p.pb for p in peers])
        avg_ps = np.mean([p.ps for p in peers])
        avg_ev_ebitda = np.mean([p.ev_ebitda for p in peers])
        
        # 基于各倍数计算估值
        value_pe = stock.eps * avg_pe
        value_pb = stock.bps * avg_pb
        value_ps = stock.revenue_per_share * avg_ps
        value_ev_ebitda = stock.ebitda * avg_ev_ebitda - stock.net_debt
        
        # 取中位数作为合理估值
        return np.median([value_pe, value_pb, value_ps, value_ev_ebitda])
    
    @staticmethod
    def historical_percentile_valuation(stock: Stock) -> float:
        """历史分位估值"""
        historical_pe = get_historical_pe(stock, years=10)
        historical_pb = get_historical_pb(stock, years=10)
        
        # 当前PE/PB在历史分位
        pe_percentile = percentile(stock.pe, historical_pe)
        pb_percentile = percentile(stock.pb, historical_pb)
        
        # 如果处于历史低位，认为低估
        if pe_percentile < 30 and pb_percentile < 30:
            fair_value = stock.eps * np.median(historical_pe) * 0.9
        else:
            fair_value = stock.current_price
        
        return fair_value
```

## 3. 风险评分（Risk Score）

### 3.1 风险检测引擎

```python
class RiskDetectionEngine:
    """风险检测引擎"""
    
    def analyze(self, stock: Stock) -> RiskReport:
        risks = []
        total_score = 0
        
        # 财务造假风险
        fraud_score = self._detect_fraud_risk(stock)
        if fraud_score > 50:
            risks.append({"type": "财务造假", "score": fraud_score, "detail": self._get_fraud_detail(stock)})
        total_score += fraud_score * RISK_WEIGHTS["financial_fraud"]
        
        # 退市风险
        delisting_score = self._detect_delisting_risk(stock)
        if delisting_score > 50:
            risks.append({"type": "退市", "score": delisting_score, "detail": self._get_delisting_detail(stock)})
        total_score += delisting_score * RISK_WEIGHTS["delisting"]
        
        # 现金流风险
        cashflow_score = self._detect_cashflow_risk(stock)
        if cashflow_score > 50:
            risks.append({"type": "现金流断裂", "score": cashflow_score, "detail": self._get_cashflow_detail(stock)})
        total_score += cashflow_score * RISK_WEIGHTS["cashflow"]
        
        # 债务违约风险
        debt_score = self._detect_debt_risk(stock)
        if debt_score > 50:
            risks.append({"type": "债务违约", "score": debt_score, "detail": self._get_debt_detail(stock)})
        total_score += debt_score * RISK_WEIGHTS["debt_default"]
        
        # 商誉风险
        goodwill_score = self._detect_goodwill_risk(stock)
        if goodwill_score > 50:
            risks.append({"type": "商誉暴雷", "score": goodwill_score, "detail": self._get_goodwill_detail(stock)})
        total_score += goodwill_score * RISK_WEIGHTS["goodwill"]
        
        # 诉讼风险
        litigation_score = self._detect_litigation_risk(stock)
        if litigation_score > 50:
            risks.append({"type": "诉讼", "score": litigation_score, "detail": self._get_litigation_detail(stock)})
        total_score += litigation_score * RISK_WEIGHTS["litigation"]
        
        # 监管调查风险
        regulatory_score = self._detect_regulatory_risk(stock)
        if regulatory_score > 50:
            risks.append({"type": "监管调查", "score": regulatory_score, "detail": self._get_regulatory_detail(stock)})
        total_score += regulatory_score * RISK_WEIGHTS["regulatory"]
        
        # 管理层风险
        management_score = self._detect_management_risk(stock)
        if management_score > 50:
            risks.append({"type": "管理层", "score": management_score, "detail": self._get_management_detail(stock)})
        total_score += management_score * RISK_WEIGHTS["management"]
        
        # 关联交易风险
        related_party_score = self._detect_related_party_risk(stock)
        if related_party_score > 50:
            risks.append({"type": "关联交易", "score": related_party_score, "detail": self._get_related_party_detail(stock)})
        total_score += related_party_score * RISK_WEIGHTS["related_party"]
        
        # 减持风险
        reduction_score = self._detect_reduction_risk(stock)
        if reduction_score > 50:
            risks.append({"type": "大股东减持", "score": reduction_score, "detail": self._get_reduction_detail(stock)})
        total_score += reduction_score * RISK_WEIGHTS["reduction"]
        
        # 股权质押风险
        pledge_score = self._detect_pledge_risk(stock)
        if pledge_score > 50:
            risks.append({"type": "股权质押", "score": pledge_score, "detail": self._get_pledge_detail(stock)})
        total_score += pledge_score * RISK_WEIGHTS["pledge"]
        
        return RiskReport(
            score=min(100, int(total_score)),
            risks=risks,
            status=self._score_to_status(total_score),
            conclusion=self._generate_risk_conclusion(risks)
        )
    
    def _detect_fraud_risk(self, stock: Stock) -> int:
        """财务造假风险检测"""
        score = 0
        
        # 1. 利润与经营现金流背离
        if stock.ocf_to_net_income < 0.5 and stock.ocf_to_net_income > 0:
            score += 30
        elif stock.ocf_to_net_income < 0:
            score += 50
        
        # 2. 应收账款异常增长
        if stock.receivable_growth > stock.revenue_growth * 2:
            score += 20
        
        # 3. 存货异常增长
        if stock.inventory_growth > stock.revenue_growth * 2:
            score += 15
        
        # 4. 毛利率异常高于行业
        if stock.gross_margin > stock.industry_avg_gross_margin * 1.5:
            score += 10
        
        # 5. 其他应收款占比高
        if stock.other_receivables_ratio > 0.1:
            score += 15
        
        # 6. 在建工程长期不转固
        if stock.construction_in_progress_years > 3:
            score += 10
        
        return min(100, score)
    
    def _detect_debt_risk(self, stock: Stock) -> int:
        """债务违约风险检测"""
        score = 0
        
        # 1. 利息覆盖倍数
        if stock.interest_coverage < 1:
            score += 50
        elif stock.interest_coverage < 1.5:
            score += 30
        elif stock.interest_coverage < 3:
            score += 15
        
        # 2. 资产负债率
        if stock.debt_ratio > 0.7:
            score += 30
        elif stock.debt_ratio > 0.6:
            score += 20
        elif stock.debt_ratio > 0.5:
            score += 10
        
        # 3. 短期债务占比
        if stock.short_term_debt_ratio > 0.6:
            score += 20
        
        # 4. 有息负债/EBITDA
        if stock.interest_bearing_debt_to_ebitda > 5:
            score += 30
        elif stock.interest_bearing_debt_to_ebitda > 3:
            score += 15
        
        # 5. 经营现金流无法覆盖短期债务
        if stock.ocf_to_short_term_debt < 0.3:
            score += 20
        
        return min(100, score)
```

## 4. 综合评分计算

```python
class CompositeScorer:
    """综合评分计算器"""
    
    def calculate(self, stock: Stock) -> CompositeScore:
        # 获取各维度评分
        quality_score = self.quality_engine.calculate(stock)
        value_score = self.value_engine.calculate(stock)
        risk_score = self.risk_engine.calculate(stock)
        sentiment_score = self.sentiment_engine.calculate(stock)
        
        # 综合评分（风险优先）
        composite = (
            quality_score.score * 0.25 +
            value_score.score * 0.25 -
            risk_score.score * 0.35 +
            (sentiment_score.score - 50) * 0.15  # 情绪偏离中性程度
        )
        
        # 确保范围在0-100
        composite = max(0, min(100, composite))
        
        # 决策
        action = self._decide(composite, risk_score.score)
        
        return CompositeScore(
            composite_score=int(composite),
            quality_score=quality_score.score,
            value_score=value_score.score,
            risk_score=risk_score.score,
            sentiment_score=sentiment_score.score,
            action=action,
            reason=self._generate_reason(quality_score, value_score, risk_score)
        )
    
    def _decide(self, composite: float, risk_score: int) -> str:
        """投资决策"""
        # 风险优先原则
        if risk_score >= 80:
            return "SELL"
        if risk_score >= 60:
            return "WATCH"
        
        # 综合评分决策
        if composite >= 70:
            return "BUY"
        elif composite >= 40:
            return "WATCH"
        else:
            return "SELL"
```

## 5. 评分等级映射

| 评分区间 | 等级 | 颜色 | 含义 |
|----------|------|------|------|
| 90-100 | S | 🟢 | 极其优秀 |
| 80-89 | A | 🟢 | 优秀 |
| 70-79 | B+ | 🟡 | 良好 |
| 60-69 | B | 🟡 | 中等偏上 |
| 50-59 | C+ | 🟠 | 中等 |
| 40-49 | C | 🟠 | 中等偏下 |
| 30-39 | D+ | 🔴 | 较差 |
| 20-29 | D | 🔴 | 差 |
| 0-19 | F | 🔴 | 极差 |