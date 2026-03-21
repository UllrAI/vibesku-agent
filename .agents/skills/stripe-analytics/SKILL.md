---
name: stripe-analytics
description: |
  从 Stripe 获取网站运营数据并生成分析报告。提供收入概览、客户增长、订阅分析（MRR/ARR/Churn）、
  退款分析、产品表现、余额与手续费等运营指标。直接调用 api.stripe.com，无第三方依赖。
  Use this skill whenever the user mentions: Stripe 运营数据、收入分析、MRR、ARR、订阅分析、
  客户增长、退款率、churn rate、Stripe dashboard、Stripe 报表、revenue analytics、
  subscription metrics、payment analytics、运营报告、收入报告。
  Also trigger when the user asks about website revenue, SaaS metrics, recurring revenue,
  customer churn, payment success rate, or any operational analytics that could come from Stripe.
user-invocable: true
metadata:
  openclaw:
    emoji: 📊
    requires:
      bins:
        - python3
    files:
      - "scripts/*"
---

# Stripe 运营分析

从 Stripe 账户直接获取运营数据，生成结构化的分析报告，帮助用户快速了解业务健康状况。

所有请求直接访问 `https://api.stripe.com/v1`，仅使用 Python 标准库，无需安装任何依赖。

## 前置检查

每次执行分析命令前，先检查凭证是否已配置：

```bash
test -f ~/.config/stripe-analytics/.env && echo "CREDENTIALS_OK" || echo "NO_CREDENTIALS"
```

- 如果 `CREDENTIALS_OK`：直接运行分析命令。
- 如果 `NO_CREDENTIALS`：引导用户完成 setup 流程（见下方）。

**不要直接读取 `~/.config/stripe-analytics/.env` 文件内容**，凭证由脚本内部加载。

## 首次配置（Setup）

1. 让用户从 https://dashboard.stripe.com/apikeys 获取 Secret Key
2. 运行 setup 命令保存凭证（密钥通过环境变量传入，避免泄露到 shell 历史）：

```bash
STRIPE_SETUP_KEY='sk_live_...' python3 <skill-dir>/scripts/stripe_analytics.py setup
```

或通过命令行参数（用户明确要求时）：

```bash
python3 <skill-dir>/scripts/stripe_analytics.py setup --key sk_test_...
```

Setup 会自动：
- 验证密钥有效性（调用 /v1/balance）
- 将密钥保存到 `~/.config/stripe-analytics/.env`（权限 0600，仅用户可读）
- 返回账户余额信息确认连接成功

3. 验证配置：

```bash
python3 <skill-dir>/scripts/stripe_analytics.py check
```

## 脚本路径

所有命令通过以下脚本执行：

```
python3 <skill-dir>/scripts/stripe_analytics.py <command> [options]
```

其中 `<skill-dir>` 是此 skill 所在目录的绝对路径。

凭证加载优先级：`~/.config/stripe-analytics/.env` > `STRIPE_SECRET_KEY` 环境变量。

## 可用命令

### setup — 首次配置

保存并验证 Stripe 密钥，见上方"首次配置"。

### check — 验证凭证

确认已保存的密钥仍然有效。

```bash
python3 <skill-dir>/scripts/stripe_analytics.py check
```

### overview — 运营全景仪表盘

一次性获取所有关键指标的综合概览，适合快速了解整体运营状况。

```bash
python3 <skill-dir>/scripts/stripe_analytics.py overview --days 30
```

输出包含：收入、客户、订阅（MRR/ARR）、退款、支付健康度五大板块。

### revenue — 收入分析

详细的收入数据，包含日均收入、每笔均额和按日拆分。

```bash
# 最近 30 天收入
python3 <skill-dir>/scripts/stripe_analytics.py revenue --days 30

# 指定日期范围
python3 <skill-dir>/scripts/stripe_analytics.py revenue --start 2025-01-01 --end 2025-01-31

# 不显示每日明细
python3 <skill-dir>/scripts/stripe_analytics.py revenue --days 7 --no-daily
```

### customers — 客户增长

新客户数量和按周的增长趋势。

```bash
python3 <skill-dir>/scripts/stripe_analytics.py customers --days 30
```

### subscriptions — 订阅与 MRR

订阅状态分布、MRR/ARR 计算、30 天流失率。

```bash
python3 <skill-dir>/scripts/stripe_analytics.py subscriptions
```

输出示例：
- Active / Trialing / Past due / Canceled 数量
- MRR（月度经常性收入）
- ARR（年度经常性收入）
- 30 天 Churn Rate

### refunds — 退款分析

退款数量、金额、占比和原因分布。

```bash
python3 <skill-dir>/scripts/stripe_analytics.py refunds --days 30
```

### products — 产品表现

按产品维度的收入和订单分布（基于 Invoice 数据）。

```bash
python3 <skill-dir>/scripts/stripe_analytics.py products --days 30
```

### balance — 余额与手续费

余额交易汇总，包含 Gross / Fee / Net 以及手续费率和按类型拆分。

```bash
python3 <skill-dir>/scripts/stripe_analytics.py balance --days 30
```

### mrr-trend — MRR 月度趋势

按月展示新增订阅、取消订阅、净增长和新增 MRR。

```bash
python3 <skill-dir>/scripts/stripe_analytics.py mrr-trend
```

## 通用参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--days N` | 回溯天数 | 30 |
| `--start YYYY-MM-DD` | 起始日期（覆盖 --days） | — |
| `--end YYYY-MM-DD` | 结束日期 | 今天 |
| `--json` | 输出原始 JSON（方便程序化处理） | false |
| `--max-items N` | 每类资源最大拉取条数 | 500 |
| `--tz ZONE` | 时区，影响日期边界和分组（偏移量如 `+8`/`-5`，或别名：CST, UTC, EST, PST, JST） | CST (UTC+8) |

## 使用场景指南

根据用户的问题选择合适的命令：

| 用户想知道 | 推荐命令 |
|-----------|---------|
| "网站最近收入怎么样" | `overview` 或 `revenue` |
| "这个月新增了多少用户" | `customers` |
| "MRR 是多少，趋势如何" | `subscriptions` + `mrr-trend` |
| "退款情况严不严重" | `refunds` |
| "哪个产品卖得最好" | `products` |
| "手续费花了多少" | `balance` |
| "给我一份完整的运营报告" | `overview`，然后按需深入各子命令 |

当用户要求"完整运营报告"时，先运行 `overview` 获取全景数据，再根据需要深入具体模块。用用户使用的语言呈现分析结果和建议。

## 输出格式

- 默认输出格式化表格，便于快速阅读
- 加 `--json` 输出结构化 JSON，适合导入到其他工具或做进一步分析
- 金额自动从"分"转换为"元"显示（如 USD、EUR），日元等无小数货币直接显示

## 注意事项

- Stripe API 有速率限制，`--max-items` 默认 500 通常够用；如数据量很大可适当调高
- 免费账户和受限 API key 可能无法访问所有端点
- MRR 计算基于当前活跃订阅的价格，属于快照值而非精确的会计数字
- Churn rate 为近 30 天简化计算：已取消 / (活跃 + 已取消)
