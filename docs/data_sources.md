# 数据源体系说明

## 1. 数据可信度评分系统

### A级数据源（官方机构）- 可信度权重：0.95

| 来源 | 数据类型 | 覆盖市场 | 更新频率 | 接入方式 |
|------|---------|---------|---------|---------|
| 上海证券交易所 | 交易数据、公告、财报 | A股 | 实时 | API |
| 深圳证券交易所 | 交易数据、公告、财报 | A股 | 实时 | API |
| 北京证券交易所 | 交易数据、公告、财报 | 北交所 | 实时 | API |
| 香港交易所 | 交易数据、公告 | 港股 | 实时 | API |
| 纳斯达克 | 交易数据 | 美股 | 实时 | API |
| 纽交所 | 交易数据 | 美股 | 实时 | API |
| 韩国交易所 | 交易数据 | 韩股 | 实时 | API |
| 东京交易所 | 交易数据 | 日股 | 实时 | API |
| SEC EDGAR | 公告、文件 | 美股 | 实时 | API |
| 中国证监会 | 监管公告、处罚 | A股 | 每日 | 爬虫 |
| 中国人民银行 | 货币政策、M0-M2 | 中国 | 月度 | API |
| 美联储 | 利率决议、资产负债表 | 美国 | 实时 | API |
| 国家统计局 | GDP、CPI、PPI | 中国 | 月度/季度 | API |
| Bureau of Labor Statistics | 就业数据、CPI | 美国 | 月度 | API |
| IMF | 全球经济数据 | 全球 | 季度 | API |
| World Bank | 发展数据 | 全球 | 年度 | API |

### B级数据源（商业数据商）- 可信度权重：0.85

| 来源 | 数据类型 | 覆盖市场 | 更新频率 | 接入方式 |
|------|---------|---------|---------|---------|
| Bloomberg | 全市场数据 | 全球 | 实时 | 终端/API |
| Reuters | 新闻、报价 | 全球 | 实时 | API |
| FactSet | 财务数据、估值 | 全球 | 每日 | API |
| Morningstar | 基金、股票数据 | 全球 | 每日 | API |
| S&P Global | 评级、财务 | 全球 | 每日 | API |
| Wind | 中国金融数据 | 中国 | 实时 | 终端/API |
| iFinD | 中国金融数据 | 中国 | 实时 | 插件/API |
| Yahoo Finance | 财务数据、报价 | 全球 | 实时 | API |
| Alpha Vantage | 股票、外汇数据 | 全球 | 实时 | API |

### C级数据源（主流财经媒体）- 可信度权重：0.60

| 来源 | 数据类型 | 覆盖市场 | 更新频率 | 接入方式 |
|------|---------|---------|---------|---------|
| 财联社 | 电报、新闻 | 中国 | 实时 | 爬虫/API |
| 证券时报 | 新闻、公告 | 中国 | 实时 | 爬虫 |
| 第一财经 | 新闻、数据 | 中国 | 实时 | 爬虫 |
| CNBC | 新闻、分析 | 美国 | 实时 | 爬虫/API |
| Wall Street Journal | 新闻、评论 | 全球 | 实时 | 爬虫/API |
| Financial Times | 新闻、分析 | 全球 | 实时 | 爬虫/API |
| 经济参考报 | 宏观分析 | 中国 | 每日 | 爬虫 |

### D级数据源（社交媒体）- 可信度权重：0.30

| 来源 | 数据类型 | 覆盖市场 | 更新频率 | 接入方式 |
|------|---------|---------|---------|---------|
| Reddit (r/wallstreetbets) | 讨论、情绪 | 美股 | 实时 | API |
| X/Twitter | 讨论、情绪 | 全球 | 实时 | API |
| 雪球 | 讨论、情绪 | 中国 | 实时 | 爬虫/API |
| 股吧 | 讨论、情绪 | A股 | 实时 | 爬虫 |
| Seeking Alpha | 讨论、文章 | 美股 | 实时 | 爬虫 |
| Yahoo Finance 讨论区 | 讨论 | 美股 | 实时 | 爬虫 |

## 2. 多源交叉验证机制

### 2.1 验证流程

```
数据A (权重0.95) ──┐
                   ├──→ 交叉验证 → 可信度评分 → 数据入库
数据B (权重0.85) ──┤
                   │
数据C (权重0.60) ──┘
```

### 2.2 可信度计算

```python
def calculate_credibility(data_points: List[DataPoint]) -> float:
    """
    计算数据可信度
    
    规则：
    1. 如果3个A级数据源一致 → 可信度 = 0.99
    2. 如果2个A级 + 1个B级一致 → 可信度 = 0.95
    3. 如果1个A级 + 2个B级一致 → 可信度 = 0.90
    4. 如果3个B级一致 → 可信度 = 0.85
    5. 如果数据冲突 → 取加权平均，可信度降低
    6. 如果只有C/D级数据源 → 最高可信度 = 0.60
    """
    
    # 按数据源等级分组
    a_level = [dp for dp in data_points if dp.source_level == 'A']
    b_level = [dp for dp in data_points if dp.source_level == 'B']
    c_level = [dp for dp in data_points if dp.source_level == 'C']
    d_level = [dp for dp in data_points if dp.source_level == 'D']
    
    # 检查一致性
    all_values = [dp.value for dp in data_points]
    std_dev = np.std(all_values)
    
    if std_dev < 0.01:  # 基本一致
        if len(a_level) >= 3:
            return 0.99
        elif len(a_level) >= 2 and len(b_level) >= 1:
            return 0.95
        elif len(a_level) >= 1 and len(b_level) >= 2:
            return 0.90
        elif len(b_level) >= 3:
            return 0.85
    
    # 数据冲突，加权平均
    weighted_sum = sum(dp.value * dp.source_weight for dp in data_points)
    total_weight = sum(dp.source_weight for dp in data_points)
    consensus = weighted_sum / total_weight
    
    # 冲突降低可信度
    conflict_penalty = min(0.3, std_dev * 10)
    base_credibility = max([dp.source_weight for dp in data_points])
    
    return max(0.3, base_credibility - conflict_penalty)
```

## 3. 宏观指标数据源

### 3.1 中国宏观数据

| 指标 | 主要来源 | 备用来源 | 更新频率 |
|------|---------|---------|---------|
| GDP | 国家统计局 | IMF/World Bank | 季度 |
| CPI | 国家统计局 | 财联社 | 月度 |
| Core CPI | 国家统计局 | - | 月度 |
| PPI | 国家统计局 | - | 月度 |
| PMI | 国家统计局 | 财新PMI | 月度 |
| M0/M1/M2 | 中国人民银行 | - | 月度 |
| 社会融资规模 | 中国人民银行 | - | 月度 |
| 新增贷款 | 中国人民银行 | - | 月度 |
| 失业率 | 国家统计局 | - | 月度 |
| 工业增加值 | 国家统计局 | - | 月度 |
| 固定资产投资 | 国家统计局 | - | 月度 |
| 房地产销售 | 国家统计局 | 中指院 | 月度 |
| 出口/进口 | 海关总署 | - | 月度 |
| 外汇储备 | 国家外汇管理局 | IMF | 月度 |

### 3.2 美国宏观数据

| 指标 | 主要来源 | 备用来源 | 更新频率 |
|------|---------|---------|---------|
| GDP | BEA | IMF | 季度 |
| CPI | BLS | 财联社 | 月度 |
| Core CPI | BLS | - | 月度 |
| PPI | BLS | - | 月度 |
| ISM | ISM | - | 月度 |
| 非农就业 | BLS | ADP | 月度 |
| 失业率 | BLS | - | 月度 |
| 利率决议 | 美联储 | - | 实时 |
| 美联储资产负债表 | 美联储 | - | 每周 |
| 财政赤字 | 财政部 | CBO | 月度 |
| 国债规模 | 财政部 | - | 实时 |

### 3.3 其他主要经济体

| 国家 | 央行 | 统计局 | 主要指标 |
|------|------|--------|---------|
| 日本 | 日本央行 | 总务省 | GDP、CPI、失业率、利率决议 |
| 韩国 | 韩国央行 | 韩国统计厅 | GDP、CPI、失业率、利率决议 |
| 欧盟 | 欧洲央行 | Eurostat | GDP、CPI、失业率、利率决议 |
| 英国 | 英格兰银行 | ONS | GDP、CPI、失业率、利率决议 |
| 印度 | 印度储备银行 | MOSPI | GDP、CPI、利率决议 |
| 新加坡 | 新加坡金融管理局 | 新加坡统计局 | GDP、CPI、失业率 |
| 澳大利亚 | 澳大利亚央行 | ABS | GDP、CPI、失业率、利率决议 |
| 加拿大 | 加拿大央行 | 加拿大统计局 | GDP、CPI、失业率、利率决议 |

## 4. 全球流动性监控数据源

| 指标 | 来源 | 更新频率 |
|------|------|---------|
| 美联储资产负债表 | 美联储 | 每周 |
| 中国央行资产负债表 | 中国人民银行 | 月度 |
| 日本央行资产负债表 | 日本央行 | 月度 |
| 欧洲央行资产负债表 | 欧洲央行 | 月度 |
| 逆回购余额 | 各央行 | 每日 |
| SOFR | 纽约联储 | 每日 |
| 美元流动性指数 | Bloomberg | 实时 |
| 全球流动性指数 | IMF | 季度 |

## 5. 利率监控数据源

| 国家/地区 | 央行 | 政策利率 | 2Y/5Y/10Y/30Y国债 | 利差数据 |
|----------|------|---------|-------------------|---------|
| 美国 | 美联储 | 美联储官网 | 美国财政部 | Bloomberg |
| 中国 | 中国人民银行 | 央行官网 | 中债登 | Wind |
| 日本 | 日本央行 | 日银官网 | 日本财务省 | Bloomberg |
| 韩国 | 韩国央行 | 央行官网 | 韩国交易所 | Bloomberg |
| 欧盟 | 欧洲央行 | 央行官网 | 欧盟统计局 | Bloomberg |
| 英国 | 英格兰银行 | 央行官网 | 英国债务管理局 | Bloomberg |

## 6. 债券市场监控数据源

| 指标 | 来源 | 更新频率 |
|------|------|---------|
| 美国国债收益率 | 美国财政部 | 实时 |
| 中国国债收益率 | 中债登 | 实时 |
| 信用利差 | Bloomberg/Markit | 实时 |
| 垃圾债利差 | Bloomberg | 实时 |
| 企业债利差 | Bloomberg | 实时 |
| 国债波动率 | MOVE Index (ICE) | 实时 |
| 全球债券指数 | Bloomberg Barclays | 每日 |

## 7. 个股财务数据源

| 数据类型 | 主要来源 | 备用来源 | 覆盖 |
|----------|---------|---------|------|
| 基础信息 | 交易所 | Bloomberg | 全部 |
| 财务报表 | 交易所/EDGAR | Wind/FactSet | 全部 |
| 财务指标 | FactSet | Morningstar | 全部 |
| 分析师预测 | FactSet | Bloomberg | 全部 |
| 历史价格 | 交易所 | Yahoo Finance | 全部 |
| 分红数据 | 交易所 | Yahoo Finance | 全部 |
| 股东信息 | 交易所 | Wind | 全部 |
| 股权质押 | 交易所 | Wind | A股/港股 |
| 关联交易 | 交易所 | 天眼查 | A股/港股 |
| 法律诉讼 | 交易所 | 天眼查 | A股/港股 |
| 管理层信息 | 公司公告 | Bloomberg | 全部 |

## 8. 新闻与舆情数据源

| 数据类型 | 来源 | 覆盖 | 语言 |
|----------|------|------|------|
| 官方公告 | 交易所/SEC/EDGAR | 全部 | 多语言 |
| 财报电话会 | 公司IR/Seeking Alpha | 美股 | 英文 |
| 投资者纪要 | 公司IR | 全部 | 多语言 |
| 财经新闻 | Bloomberg/Reuters | 全球 | 英文 |
| 中文新闻 | 财联社/证券时报/第一财经 | 中国 | 中文 |
| 英文新闻 | CNBC/WSJ/FT | 全球 | 英文 |
| 社交讨论 | Reddit/X | 全球 | 英文 |
| 中文讨论 | 雪球/股吧 | 中国 | 中文 |
| 分析文章 | Seeking Alpha | 美股 | 英文 |
| 讨论区 | Yahoo Finance | 美股 | 英文 |

## 9. 数据更新频率配置

```yaml
# config/data_update.yaml
update_schedule:
  real_time:
    - stock_price       # 实时股价
    - order_book        # 订单簿
    - news_ticker       # 新闻快讯
  
  every_5_minutes:
    - market_index      # 主要指数
    - sentiment_score   # 情绪指数
    - liquidity_index   # 流动性指数
  
  every_30_minutes:
    - technical_indicators  # 技术指标
    - option_data           # 期权数据
  
  hourly:
    - social_sentiment  # 社交情绪
    - volume_analysis   # 成交量分析
  
  daily:
    - stock_financials      # 个股财务
    - macro_indicators      # 宏观指标
    - yield_curve           # 收益率曲线
    - credit_spread         # 信用利差
    - risk_metrics          # 风险指标
  
  weekly:
    - fed_balance_sheet     # 美联储资产负债表
    - fund_flow             # 资金流向
    - institutional_holdings  # 机构持仓
  
  monthly:
    - gdp_data              # GDP数据
    - cpi_ppi_data          # 通胀数据
    - employment_data       # 就业数据
    - trade_data            # 贸易数据
  
  quarterly:
    - financial_reports     # 财报
    - industry_data         # 行业数据
    - balance_sheet         # 资产负债表详情
  
  annual:
    - annual_report         # 年报
    - historical_analysis   # 历史分析
```