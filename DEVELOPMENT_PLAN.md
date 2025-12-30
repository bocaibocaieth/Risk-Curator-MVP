# DeFi Risk Curator MVP - 开发计划

## 项目结构

```
Risk-Curator-MVP/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 入口
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   ├── models/            # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── asset.py
│   │   │   ├── protocol.py
│   │   │   ├── rating.py
│   │   │   ├── alert.py
│   │   │   └── price.py
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── asset.py
│   │   │   ├── rating.py
│   │   │   └── alert.py
│   │   ├── api/               # API 路由
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── assets.py
│   │   │       ├── ratings.py
│   │   │       ├── alerts.py
│   │   │       └── monitor.py
│   │   └── services/          # 业务逻辑
│   │       ├── __init__.py
│   │       ├── rating_calculator.py
│   │       ├── price_service.py
│   │       ├── monitor_service.py
│   │       └── alert_service.py
│   ├── alembic/               # 数据库迁移
│   ├── tests/                 # 测试
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                   # Next.js 前端
│   ├── app/                   # App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx           # Dashboard
│   │   ├── assets/
│   │   ├── ratings/
│   │   ├── alerts/
│   │   └── settings/
│   ├── components/
│   │   ├── ui/                # shadcn/ui
│   │   ├── layout/
│   │   ├── dashboard/
│   │   ├── rating/
│   │   └── alert/
│   ├── lib/
│   │   ├── api.ts
│   │   └── utils.ts
│   ├── types/
│   └── package.json
│
├── docker-compose.yml          # 本地开发环境
├── DEVELOPMENT_PLAN.md
└── README.md
```

---

## 开发阶段规划

### Phase 1: 后端基础架构 (Module 1 & 2)

#### 1.1 项目初始化
- [ ] 创建后端项目结构
- [ ] 配置 FastAPI 应用入口
- [ ] 设置 Pydantic Settings 配置管理
- [ ] 配置 SQLAlchemy 2.0 异步连接
- [ ] 设置 Alembic 数据库迁移

#### 1.2 数据库模型
- [ ] 创建 Asset 模型 (资产表)
- [ ] 创建 Protocol 模型 (协议表)
- [ ] 创建 AssetRating 模型 (资产评级)
- [ ] 创建 MarketRating 模型 (市场评级)
- [ ] 创建 PriceHistory 模型 (价格历史)
- [ ] 创建 AlertConfig 模型 (告警配置)
- [ ] 创建 AlertHistory 模型 (告警历史)
- [ ] 生成初始迁移脚本

#### 1.3 评级系统核心
- [ ] 实现 RatingCalculator 服务
  - score_to_grade() 转换函数
  - calculate_issuer_risk() 发行人风险
  - calculate_operational_risk() 运营风险
  - calculate_asset_rating() 资产评级
  - calculate_credit_enhancement() 信用增强
  - get_vault_eligibility() Vault适用性
- [ ] 创建评级相关 Pydantic schemas
- [ ] 实现评级 API endpoints

#### 1.4 资产管理 API
- [ ] GET /api/v1/assets - 资产列表
- [ ] POST /api/v1/assets - 创建资产
- [ ] GET /api/v1/assets/{id} - 资产详情
- [ ] PUT /api/v1/assets/{id} - 更新资产
- [ ] DELETE /api/v1/assets/{id} - 删除资产

#### 1.5 评级管理 API
- [ ] POST /api/v1/ratings/assets - 创建评级
- [ ] GET /api/v1/ratings/assets - 评级列表
- [ ] GET /api/v1/ratings/assets/{id} - 评级详情
- [ ] PUT /api/v1/ratings/assets/{id} - 更新评级

---

### Phase 2: 监控与告警 (Module 3 & 4)

#### 2.1 价格服务
- [ ] 实现 CoinGecko API 集成
- [ ] 实现 DeFiLlama Prices API 集成
- [ ] 添加内存缓存 (60秒 TTL)
- [ ] 批量价格获取
- [ ] 错误处理和重试逻辑

#### 2.2 TVL 服务
- [ ] 获取协议 TVL
- [ ] 获取协议详情

#### 2.3 监控服务
- [ ] 价格偏离检查
- [ ] 稳定币脱锚检查
- [ ] 后台监控循环 (每分钟)
- [ ] 价格历史记录

#### 2.4 监控 API
- [ ] GET /api/v1/monitor/prices/{asset_id}
- [ ] GET /api/v1/monitor/prices (批量)
- [ ] GET /api/v1/monitor/tvl/{protocol}
- [ ] POST /api/v1/monitor/check (手动触发)

#### 2.5 Telegram 告警服务
- [ ] 发送消息功能
- [ ] 格式化告警 (HTML格式)
- [ ] 严重级别区分
- [ ] 冷却时间控制

#### 2.6 告警 API
- [ ] POST /api/v1/alerts/configs - 创建配置
- [ ] GET /api/v1/alerts/configs - 配置列表
- [ ] PUT /api/v1/alerts/configs/{id} - 更新配置
- [ ] DELETE /api/v1/alerts/configs/{id} - 删除配置
- [ ] POST /api/v1/alerts/configs/{id}/test - 测试
- [ ] GET /api/v1/alerts/history - 告警历史

---

### Phase 3: 前端 Dashboard (Module 5)

#### 3.1 项目初始化
- [ ] 创建 Next.js 14 项目
- [ ] 配置 Tailwind CSS
- [ ] 安装 shadcn/ui 组件
- [ ] 安装 React Query + Recharts
- [ ] 配置 API 客户端

#### 3.2 布局组件
- [ ] Sidebar 导航
- [ ] Header 组件
- [ ] 响应式布局

#### 3.3 Dashboard 首页
- [ ] 统计卡片 (监控资产、AUM、告警、评级)
- [ ] 评级分布饼图
- [ ] 最近告警列表
- [ ] 资产价格表格

#### 3.4 资产页面
- [ ] 资产列表
- [ ] 资产详情
- [ ] 添加资产表单

#### 3.5 评级页面
- [ ] 评级列表
- [ ] 评级详情
- [ ] 新建评级表单 (三步)
  - Step 1: 选择资产
  - Step 2: 填写评分 (Slider 1-6)
  - Step 3: 确认提交

#### 3.6 告警页面
- [ ] 告警配置列表
- [ ] 创建告警 Dialog
- [ ] 告警历史表格

---

### Phase 4: 部署 (Module 6)

#### 4.1 后端部署 (Railway)
- [ ] Dockerfile
- [ ] railway.json 配置
- [ ] 环境变量配置
- [ ] PostgreSQL 数据库
- [ ] 健康检查 endpoint

#### 4.2 前端部署 (Vercel)
- [ ] vercel.json 配置
- [ ] 环境变量
- [ ] API 代理配置

#### 4.3 数据库
- [ ] Alembic 迁移脚本
- [ ] Seed 数据脚本

#### 4.4 CI/CD (可选)
- [ ] GitHub Actions
- [ ] 代码检查
- [ ] 自动部署

---

## 技术决策

### 后端
- **Python 3.11+**: AI辅助编程效果好，Web3库成熟
- **FastAPI**: 简单快速，自动生成API文档
- **SQLAlchemy 2.0**: 异步支持，类型安全
- **Pydantic v2**: 数据验证，配置管理

### 前端
- **Next.js 14**: Vercel免费部署，App Router
- **Tailwind CSS**: 快速样式开发
- **shadcn/ui**: 高质量UI组件
- **React Query**: 服务端状态管理

### 数据库
- **PostgreSQL**: 时序数据支持，免费tier足够
- **Redis**: 缓存价格数据 (可选，MVP可用内存缓存)

---

## MVP 范围

### 必须有 ✅
- 资产管理 CRUD
- 三层资产评级计算
- 价格监控 (CoinGecko/DeFiLlama)
- Telegram 告警
- 基础 Dashboard

### 可以有 ⭐
- 协议 TVL 监控
- 市场评级 (LLTV)
- 多链支持
- 告警历史分析

### 不做 ❌
- 自动再平衡
- 链上交易执行
- 完整 Vault 管理
- 多用户/多租户

---

## 开发顺序建议

```
Week 1: Phase 1 (后端基础 + 评级系统)
  ├── Day 1-2: 项目结构 + 数据库模型
  ├── Day 3-4: 评级计算逻辑 + API
  └── Day 5: 资产管理 API

Week 2: Phase 2 (监控 + 告警)
  ├── Day 6-7: 价格服务 + 监控
  └── Day 8-10: 告警系统 + Telegram

Week 3: Phase 3 (前端)
  ├── Day 11-12: 布局 + Dashboard
  ├── Day 13-14: 评级表单
  └── Day 15: 告警配置

Week 4: Phase 4 (部署 + 优化)
  ├── Day 16: Docker + Railway
  └── Day 17: Vercel + 调试
```

---

## 下一步

准备好开始后，我们将按以下顺序进行：

1. **创建后端项目结构** - 初始化 FastAPI 项目
2. **实现数据库模型** - 所有核心表
3. **实现评级系统** - 核心业务逻辑
4. **添加监控服务** - 价格获取 + 告警
5. **创建前端** - Dashboard + 表单
6. **配置部署** - Docker + CI/CD

请确认这个计划是否符合你的预期，或者告诉我需要调整的地方。
