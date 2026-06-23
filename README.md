# Global Alpha Sentinel（全球阿尔法哨兵）

> 机构级全球金融宏观预警与价值发现系统

## 🎯 项目定位

自动化的全球金融市场监控系统，覆盖中国A股、港股、美股、韩股、日股及全球主要资产类别，提供：

- 🔴 **系统性风险** 实时预警
- 🟡 **行业风险** 智能识别
- 🟢 **个股价值** 深度发现
- 🤖 **AI投研报告** 自动生成
- 📱 **多渠道预警** 自动推送

## 🏛️ 系统定位

**机构级研究平台**

| 对标系统 | 功能覆盖 |
|---------|---------|
| Bloomberg Terminal | 实时数据与市场监控 |
| FactSet / Capital IQ | 财务分析与估值建模 |
| Wind | 中国A股全量数据 |
| Bridgewater Risk Dashboard | 宏观风险预警 |
| BlackRock Aladdin | 组合风险监控（简化版） |

## ⚡ 核心原则

### 第一原则：准确性优先于速度
- 同一指标至少验证3个数据源
- 数据冲突时自动计算可信度权重
- 禁止为实时性牺牲数据质量

### 第二原则：结论简单明了
- 禁止输出冗长分析
- 每个分析最终必须输出：`🟢 买入 / 🟡 观察 / 🔴 卖出`
- 附带：1句话原因

### 第三原则：风险优先
- 任何分析流程：先识别风险，再寻找机会
- 风险评分(Value Score)优先于估值评分

## 🗺️ 覆盖市场

| 市场类型 | 标的 |
|---------|------|
| 中国A股 | 全部A股（上证、深证、创业板、科创板） |
| 港股 | 全部港股（恒生、恒生科技） |
| 美股 | 全部美股（标普500、纳指、道指） |
| 韩股 | KOSPI、KOSDAQ |
| 日股 | 日经225、TOPIX |
| 其他 | 全球ETF、REITs、ADR、主要股指 |
| 债券 | 国债、企业债、信用债 |
| 外汇 | 主要货币对 |
| 大宗商品 | 原油、黄金、铜、农产品等 |
| 加密资产 | 仅作为风险参考因子 |

## 📊 系统架构

```
Global Alpha Sentinel
│
├── 📡 数据采集层 (Data Ingestion)
│   ├── A级数据源（交易所、公告、监管机构）
│   ├── B级数据源（Bloomberg、Reuters、FactSet）
│   ├── C级数据源（主流财经媒体）
│   └── D级数据源（社交媒体、论坛）
│
├── 🧠 AI Agent 系统 (Multi-Agent)
│   ├── 宏观研究员 (Macro Agent)
│   ├── 行业研究员 (Industry Agent)
│   ├── 财务分析师 (Financial Analyst Agent)
│   ├── 风险控制官 (Risk Officer Agent)
│   ├── 估值分析师 (Valuation Agent)
│   ├── 新闻分析师 (News Analyst Agent)
│   ├── 舆情分析师 (Sentiment Agent)
│   ├── 量化分析师 (Quant Analyst Agent)
│   ├── 组合经理 (Portfolio Manager Agent)
│   └── 首席投资官 (CIO Agent) ← 最终决策汇总
│
├── 📈 核心引擎层 (Core Engine)
│   ├── 宏观监控引擎
│   ├── 风险预警引擎
│   ├── 低估值发现引擎
│   ├── 企业质量评分引擎
│   ├── 新闻情感分析引擎
│   └── 社交情绪分析引擎
│
├── 📋 决策输出层 (Output)
│   ├── 个股分析报告
│   ├── 宏观风险预警
│   ├── 低估值排行榜
│   ├── 高风险排行榜
│   ├── AI推荐组合
│   └── AI避险组合
│
└── 🚀 推送系统 (Distribution)
    ├── Telegram
    ├── 企业微信
    ├── 微信机器人
    ├── 钉钉
    ├── 飞书
    ├── 邮件
    └── 短信
```

## 🏗️ 项目目录结构

```
global-alpha-sentinel/
├── .github/
│   └── workflows/             # CI/CD 自动化
├── docs/
│   ├── architecture.md        # 系统架构文档
│   ├── agent_system.md        # 多Agent系统设计
│   ├── data_sources.md        # 数据源体系说明
│   ├── risk_framework.md      # 风险框架定义
│   └── scoring_model.md       # 评分模型说明
├── src/
│   ├── agents/                # AI Agent 模块
│   ├── data_ingestion/        # 数据采集层
│   ├── core_engine/           # 核心引擎
│   ├── analysis/              # 分析工具
│   ├── visualization/         # 可视化Dashboard
│   └── output/                # 输出格式化
├── config/
│   ├── markets.yaml           # 市场配置
│   ├── indicators.yaml        # 指标配置
│   ├── thresholds.yaml        # 阈值配置
│   └── agents.yaml            # Agent配置
├── tests/                     # 单元测试
├── notebooks/                 # 研究笔记本
├── data/                      # 本地数据缓存
├── scripts/                   # 工具脚本
├── requirements.txt           # Python依赖
├── Dockerfile                 # 容器化
├── docker-compose.yml         # 编排
├── README.md                  # 项目说明
└── LICENSE                    # 开源协议
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Docker 24.0+
- Redis 7.0+ (缓存与消息队列)
- PostgreSQL 15+ (结构化数据)
- InfluxDB 2.0+ (时序数据)

### 安装依赖

```bash
# 克隆仓库
git clone https://github.com/leeyunzhao1-code/global-alpha-sentinel.git
cd global-alpha-sentinel

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 启动服务

```bash
# Docker 全量启动
docker-compose up -d

# 启动单个Agent
cd src/agents
python macro_agent.py
```

## 📋 输出示例

### 个股分析报告

```
微软（MSFT）

当前价格：    530美元
合理价值：    620美元
低估幅度：    17%
风险等级：    12/100
价值等级：    88/100

结论：🟢 买入

原因：现金流极强，AI业务高速增长，估值低于历史合理区间。
```

### 宏观预警报告

```
美国经济

风险等级：    82/100
状态：       🔴 高风险

原因：
- 收益率倒挂
- 失业率上升
- 信用利差扩大
- 流动性收缩

建议：
- 降低仓位至30%
- 增加现金配置
```

## 🔗 外部系统对接

| 系统 | 接口类型 | 用途 |
|------|---------|------|
| Kimi Finance API | REST API | 实时行情、技术指标 |
| Yahoo Finance | REST API | 美股财务数据 |
| iFinD | 插件 | 中国A股全量数据 |
| SEC EDGAR | 插件 | 美股公告与文件 |
| IMF | 插件 | 全球经济指标 |
| World Bank | 插件 | 发展数据 |
| 财联社 | 爬虫 | 中文新闻与电报 |
| 红迪/X/雪球 | 爬虫 | 社交情绪 |

## 📜 开源协议

MIT License © 2025 Global Alpha Sentinel Team

---

> ⚠️ **免责声明**：本系统提供的所有分析、评分、建议仅供研究参考，不构成任何投资建议。投资有风险，决策需独立判断。