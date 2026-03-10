# VibeSKU 运营自动化精简方案

> 日期：2026-03-10
> 状态：已确认
> 目标：保留框架，瘦身内容——从多目标收敛为小红书单目标闭环，稳定运行后再扩展

---

## 一、背景与动机

当前运营自动化系统在冷启动阶段就搭建了生产级全套体系（3 KR、12 Plan、4 Discord 频道、6 Cron、三层架构），导致：

- 运行不稳定，组件间耦合多、故障面广
- 功能太多无法有效迭代
- 没有跑通一个完整的"目标 → 任务 → 执行 → 反馈 → 调整"闭环

**核心策略**：保留三层架构和流程框架不变，将内容收敛到小红书单目标，先跑通一个最小闭环再扩展。

---

## 二、精简范围

### 2.1 OKR 归档

- 将 `OKR/2026-03-冷启动/` 整体移入 `OKR/_archive/2026-03-冷启动/`
- 指标字典归档（当前指标面向注册/激活/付费，与小红书无关）
- Tasks / Reports / Deliverables 中的历史文件移入对应 `_archive/` 子目录
- 归档后通过 `goal-to-plan` skill 重新生成小红书 KR + Plan
- 小红书内容方向在 goal-to-plan 中确定（本方案不预设）

### 2.2 Discord 频道重组：4 → 3

| 频道 | 方向 | 职责 |
|------|------|------|
| `#vibesku-cmd` | 人 → Agent | 用户下达指令：调整任务、新增 Plan、修改架构、临时指派 |
| `#vibesku-daily` | Agent → 人 | 每日任务概览 + 数据日报 + human task 确认 thread（原 daily + data 合并） |
| `#vibesku-ops` | Agent → Agent/人 | 执行日志 + 复盘/审计通知（原 ops + review 合并，可静音） |

**变更**：
- 新增 `#vibesku-cmd` 作为 vibesku Agent main session 绑定频道
- 合并 `#vibesku-data` 到 `#vibesku-daily`（数据日报和任务在同一个频道）
- 合并 `#vibesku-review` 到 `#vibesku-ops`（复盘通知作为执行日志的一部分）

### 2.3 SOUL.md 瘦身重构

**当前问题**：264 行，远超 OpenClaw 规范（~40 行），身份/规则/路由/处理逻辑全揉在一起。

**重构为**：

| 文件 | 内容 | 预期行数 |
|------|------|----------|
| `SOUL.md` | 身份、使命、原则、边界 | ~50 行 |
| `AGENTS.md` | Dispatch Rules、Post-Spawn Processing、Human Task Processing、Startup Reconciliation | ~100 行 |
| `event-handlers.md` | Event Handler 定义（On: agent_completed / human_reply / human_task_ready） | ~60 行 |
| `channel-routing.md` | 频道常量 + 路由规则（3 频道） | ~30 行 |

- Agent 启动时自动加载 `SOUL.md` + `AGENTS.md`
- reference 文件（event-handlers / channel-routing）按需引用

### 2.4 Cron 调整

| Cron | 时间 | 动作 | 理由 |
|------|------|------|------|
| `vibesku-daily-plan` | 09:00 daily | **保留** | 核心闭环：生成每日任务 |
| `vibesku-data-report-trigger` | 18:00 daily | **保留** | 核心闭环：数据反馈 |
| `vibesku-review-check` | ~~每 4h~~ → 20:00 daily | **保留，降频** | 单 KR 不需要高频，放在日报后扫描 review trigger |
| `vibesku-weekly-review` | 周五 17:00 | **保留** | 周维度回顾 |
| `vibesku-daily-audit` | 01:23 daily | **不变** | Phase 5 未实施，保持待实施状态 |
| `微博投资机会分析` | 09:00 daily | **不变** | 与运营独立 |

### 2.5 Prompt 模板适配

- `daily-ops.prompt.md`：更新 OKR 读取路径，移除冷启动特定逻辑，新 KR 生成后适配小红书数据源
- `data-report.prompt.md`：数据源从 Umami/Stripe/DB 切换为小红书 skill（`content-data` 命令），保留 PARTIAL 模式和异常检测逻辑
- `ops-review.prompt.md`：保持结构不变，适配新 KR 指标

### 2.6 Engine 配置更新

- `config.yaml`：频道 ID 从 4 个更新为 3 个（cmd / daily / ops）
- `review-check` 调度频率从 `*/4 * * * *` 改为 `0 20 * * *`
- 其余保持不变（轮询间隔 30s、并发上限 3、提醒阈值 24h/48h 等）

---

## 三、不变的部分

以下内容保持不变，确保框架完整性：

- **三层架构**：Cron（定时触发）+ Engine（确定性状态机）+ Orchestrator（语义决策）
- **任务生命周期**：planned → spawning → in_progress → review → done/failed
- **Agent 角色体系**：Builder / Ops / Data / Human
- **Handoff 协议**：what was done / where artifacts are / how to verify / known issues / what's next
- **Plan Log 回写规则**：只有执行 Agent 写，格式规范不变
- **失败处理 SOP**：P0/P1/P2 分级、自动重试、PARTIAL 模式
- **权限管理**：最小权限、只读优先、密钥轮换
- **OKR/Plan 文件结构**：index.md + Plan 独立文件（三段式：Plan/Log/Review）
- **半自动审批流**：!approve / !reject / !done / !block 命令协议

---

## 四、执行顺序

1. **归档现有内容**：OKR / Tasks / Reports / Deliverables / 指标字典 → `_archive/`
2. **Discord 频道重组**：创建 `#vibesku-cmd`，更新频道映射
3. **SOUL.md 瘦身**：拆分为 SOUL.md + AGENTS.md + reference 文件
4. **Engine 配置更新**：频道 ID、review-check 频率
5. **Cron 更新**：review-check 降频、Prompt 路径更新
6. **运营自动化方案文档更新**：反映精简后的架构
7. **调用 goal-to-plan**：生成小红书 KR + Plan + 指标
8. **Prompt 适配**：根据新 KR 和数据源更新三个 prompt 模板
9. **端到端验证**：手动触发一次完整日循环，确认闭环跑通
