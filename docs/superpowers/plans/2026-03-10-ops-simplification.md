# VibeSKU 运营自动化精简 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 保留框架，瘦身内容——归档冷启动 OKR，整理 Discord/SOUL.md/Cron，为小红书单目标闭环腾出干净的运行环境。

**Architecture:** 三层架构（Cron + Engine + Orchestrator）不变。通过归档历史内容、合并频道、拆分 SOUL.md、调整 Cron 频率来精简系统，最后通过 goal-to-plan 生成新的小红书 KR。

**Tech Stack:** Obsidian vault（文件系统直接操作）、OpenClaw cron/agent config（JSON/YAML）、Discord（手动创建频道）

**Spec:** `docs/superpowers/specs/2026-03-10-ops-simplification-design.md`

---

## Chunk 1: 归档现有内容

### Task 1: 归档 OKR 与关联文件

**Files:**
- Move: `01-Projects/ullrai/VibeSKU/Operations/OKR/2026-03-冷启动/` → `OKR/_archive/2026-03-冷启动/`
- Move: `01-Projects/ullrai/VibeSKU/Operations/Metrics/指标字典.md` → `Metrics/_archive/指标字典-冷启动.md`
- Move: `01-Projects/ullrai/VibeSKU/Operations/Tasks/2026-03-*.md` → `Tasks/_archive/`
- Move: `01-Projects/ullrai/VibeSKU/Operations/Reports/日报/2026-03-*.md` → `Reports/_archive/日报/`
- Move: `01-Projects/ullrai/VibeSKU/Operations/Reports/缺失数据源告警.md` → `Reports/_archive/`
- Move: `01-Projects/ullrai/VibeSKU/Operations/Deliverables/*.md` → `Deliverables/_archive/`
- Move: `01-Projects/ullrai/VibeSKU/Operations/Reviews/*.md` → `Reviews/_archive/`
- Move: `01-Projects/ullrai/VibeSKU/Operations/Data/日报/*.md` → `Data/_archive/日报/`

Obsidian vault base path: `/home/dev/obsidian-vault`

- [ ] **Step 1: 创建归档目录**

```bash
OPS="/home/dev/obsidian-vault/01-Projects/ullrai/VibeSKU/Operations"
mkdir -p "$OPS/OKR/_archive"
mkdir -p "$OPS/Metrics/_archive"
mkdir -p "$OPS/Tasks/_archive"
mkdir -p "$OPS/Reports/_archive/日报"
mkdir -p "$OPS/Deliverables/_archive"
mkdir -p "$OPS/Reviews/_archive"
mkdir -p "$OPS/Data/_archive/日报"
```

- [ ] **Step 2: 移动 OKR**

```bash
mv "$OPS/OKR/2026-03-冷启动" "$OPS/OKR/_archive/2026-03-冷启动"
```

- [ ] **Step 3: 归档指标字典**

```bash
mv "$OPS/Metrics/指标字典.md" "$OPS/Metrics/_archive/指标字典-冷启动.md"
```

- [ ] **Step 4: 归档 Tasks**

```bash
mv "$OPS/Tasks/2026-03-"*.md "$OPS/Tasks/_archive/"
```

- [ ] **Step 5: 归档 Reports**

```bash
mv "$OPS/Reports/日报/2026-03-"*.md "$OPS/Reports/_archive/日报/"
mv "$OPS/Reports/缺失数据源告警.md" "$OPS/Reports/_archive/"
```

- [ ] **Step 6: 归档 Deliverables、Reviews、Data**

```bash
mv "$OPS/Deliverables/"*.md "$OPS/Deliverables/_archive/"
mv "$OPS/Reviews/"*.md "$OPS/Reviews/_archive/"
mv "$OPS/Data/日报/"*.md "$OPS/Data/_archive/日报/"
```

- [ ] **Step 7: 验证归档完成**

```bash
# 确认活跃目录为空（只保留 _archive 子目录和 Prompts/Runbooks 等框架文件）
ls "$OPS/OKR/"           # 应只有 _archive/
ls "$OPS/Tasks/"         # 应只有 _archive/
ls "$OPS/Reports/日报/"  # 应为空
ls "$OPS/Deliverables/"  # 应只有 _archive/
```

Expected: 各活跃目录只剩 `_archive/` 子目录，Prompts/ 和 Runbooks/ 保持不动。

### Task 2: 清理过期的一次性 Cron 任务

**Files:**
- Modify: `/home/dev/.openclaw/cron/jobs.json`

- [ ] **Step 1: 读取 jobs.json 确认过期的 spawn 任务**

读取 `/home/dev/.openclaw/cron/jobs.json`，找到 `spawn-T-20260307-03` 和 `spawn-T-20260308-03` 这两个一次性任务（已超时/完成）。

- [ ] **Step 2: 删除过期任务**

使用 OpenClaw CLI 或直接编辑 jobs.json，移除这两个 spawn 条目。

```bash
openclaw cron delete spawn-T-20260307-03
openclaw cron delete spawn-T-20260308-03
```

如果 CLI 不支持 delete，直接编辑 JSON 文件移除对应条目。

- [ ] **Step 3: 验证**

```bash
openclaw cron list
```

Expected: 只剩 5 个 cron 任务（微博 + daily-plan + data-report + review-check + weekly-review + daily-audit）。

---

## Chunk 2: Discord 频道重组

### Task 3: 创建 #vibesku-cmd 频道并更新映射

**Files:**
- Modify: `/home/dev/vibesku-workspace/engine/config.yaml`

- [ ] **Step 1: 创建 Discord 频道（手动）**

在 Discord Server 中创建 `#vibesku-cmd` 频道。记录新频道的 Channel ID。

> 这是一个人工步骤。完成后将 Channel ID 提供给下一步。

- [ ] **Step 2: 更新 Engine config.yaml 频道映射**

修改 `/home/dev/vibesku-workspace/engine/config.yaml`：

```yaml
# Discord channels（精简后：3 频道）
channels:
  cmd: "<新频道ID>"                    # 人 → Agent 指挥频道
  daily: "1479016498684231740"         # Agent → 人（任务+数据+确认）
  ops: "1479326701917044887"           # Agent → Agent/人（执行日志+复盘）
  # data 和 review 合并到 daily 和 ops，以下保留注释供回溯
  # data: "1479016552153088080"        # [已合并到 daily]
  # review: "1479016600278667295"      # [已合并到 ops]

# Notification routing: message_type -> channel key（更新路由）
routing:
  dispatch_summary: ops
  agent_complete: ops
  quality_gate: ops
  task_blocked: ops
  error_alert: ops
  human_thread: daily
  human_reminder: daily
  daily_summary: daily
  data_report: daily           # 原 data → 合并到 daily
  data_alert: daily            # 原 data → 合并到 daily
  plan_review: ops             # 原 review → 合并到 ops
```

- [ ] **Step 3: 更新 Engine OKR 路径**

同一文件中更新 obsidian.okr_dir（归档后新 OKR 路径待 goal-to-plan 生成后确定，暂置空）：

```yaml
obsidian:
  vault_path: "/home/dev/obsidian-vault"
  tasks_dir: "01-Projects/ullrai/VibeSKU/Operations/Tasks"
  okr_dir: ""  # 待 goal-to-plan 生成新 OKR 后更新
```

- [ ] **Step 4: 验证 config.yaml 格式**

```bash
python3 -c "import yaml; yaml.safe_load(open('/home/dev/vibesku-workspace/engine/config.yaml'))" && echo "YAML valid"
```

Expected: `YAML valid`

---

## Chunk 3: SOUL.md 瘦身重构

### Task 4: 拆分 SOUL.md 为 4 个文件

**Files:**
- Rewrite: `/home/dev/vibesku-workspace/SOUL.md` （264 行 → ~50 行）
- Create: `/home/dev/vibesku-workspace/ops-rules.md`（~120 行）
- Create: `/home/dev/vibesku-workspace/event-handlers.md`（~60 行）
- Create: `/home/dev/vibesku-workspace/channel-routing.md`（~30 行）

> 注意：现有 AGENTS.md 是 OpenClaw 通用 workspace 指南（212 行），保持不动。操作规则放在独立的 reference 文件中，SOUL.md 引用它们。

- [ ] **Step 1: 备份当前 SOUL.md**

```bash
cp /home/dev/vibesku-workspace/SOUL.md /home/dev/vibesku-workspace/SOUL.md.bak.pre-simplification
```

- [ ] **Step 2: 创建 channel-routing.md**

写入 `/home/dev/vibesku-workspace/channel-routing.md`：

```markdown
# Channel Routing

所有 Discord 消息必须通过 CLI 显式发送到目标频道。

## 频道常量

| 频道 | Channel ID | 方向 | 用途 |
|------|-----------|------|------|
| #vibesku-cmd | channel:<CMD_ID> | 人 → Agent | 用户指令：调整任务、新增 Plan、修改架构 |
| #vibesku-daily | channel:1479016498684231740 | Agent → 人 | 每日任务 + 数据日报 + human task thread |
| #vibesku-ops | channel:1479326701917044887 | Agent → Agent/人 | 执行日志 + 复盘通知（可静音） |

## 发送命令

普通消息：`openclaw message send --channel discord --target "channel:<ID>" --message "<text>"`
创建 thread：`openclaw message thread create --channel discord --target "channel:<ID>" --thread-name "<name>" --message "<body>"`

## 路由规则

| 消息类型 | 目标频道 |
|----------|---------|
| 派发摘要 | #vibesku-ops |
| Agent 完成状态更新 | #vibesku-ops |
| 质量门结果 | #vibesku-ops |
| 任务 blocked / 错误告警 | #vibesku-ops |
| Plan 审查结果 | #vibesku-ops |
| Human task thread 创建 | #vibesku-daily |
| Human task 提醒 | #vibesku-daily |
| 每日总结 | #vibesku-daily |
| 数据日报 / 数据源告警 | #vibesku-daily |
```

> 注意：`<CMD_ID>` 需要在 Task 3 Step 1 创建频道后替换为实际 ID。

- [ ] **Step 3: 创建 event-handlers.md**

写入 `/home/dev/vibesku-workspace/event-handlers.md`：

```markdown
# Event Handlers (v2.5)

Engine 发送结构化事件，格式：`EVENT: {type} | task: {id} | plan: {ref} | {metadata_json}`

## 幂等性规则

- 执行前检查 state precondition（任务当前状态是否匹配预期）
- side-effect-first, status-last（先创建 thread/写 review，最后改状态）
- 创建 Discord thread 前检查是否已存在同名 thread
- 写状态前确认当前状态仍为预期值（防竞态）

## On: agent_completed

**触发**: Agent 完成，Plan Log 有新条目
**前置条件**: task status = `review`（不满足则跳过并 log）
**处理**:
1. 读取 Plan Log 新条目 + 产出物 + 验收标准
2. 质量门：检查 Handoff 5 项完整、产出物存在
3. 通过 → patch status `done`，写 Plan Review
4. 不通过 → patch status `failed`，#vibesku-ops 说明原因
5. 发简报到 #vibesku-ops

## On: human_task_ready

**触发**: human 类型任务需要创建 Discord thread
**前置条件**: task status = `planned` 或 `blocked`（不满足则跳过）
**处理**:
1. 读 Plan 文件，提取背景/状态/决策问题/选项/影响/推荐
2. 在 #vibesku-daily 创建 thread，标题 `[{task_id}] 描述`
3. patch status `assigned`

## On: human_reply

**触发**: 用户在 Discord thread 回复了 human task
**前置条件**: task status = `assigned` 且 agent_type = `human`
**去重**: 比较 metadata 中 `reply_message_id` 与 Tasks 文件的 `last_processed_reply_id`，相同则跳过
**处理**:
1. 读完整 thread 对话 + 任务目标 + Plan
2. 判断用户决策：
   - confirmed_as_asked → status `done`，写 Plan Review
   - agreed_to_alternative → status `skipped`，写 Plan Review 记录替代方案
   - needs_more_info → 在 thread 追问，保持 `assigned`，写 `last_processed_reply_id`
   - rejected → status `blocked`，写 Plan Review
3. 发简报到 #vibesku-ops
```

- [ ] **Step 4: 创建 ops-rules.md**

写入 `/home/dev/vibesku-workspace/ops-rules.md`：

```markdown
# Operations Rules

## Agent Routing

| agent_type | Route to | Typical tasks | Key tools |
|-----------|----------|---------------|-----------|
| `coding` | Builder Agent | Bug fix, feature dev, API integration | coding-agent skill, VibeSKU repo worktree |
| `ops` | Ops Agent | 内容策划、文案、小红书内容 | obsidian-mcp, xiaohongshu-skills (semi-auto) |
| `data` | Data Agent | 数据采集、日报、指标验证 | xiaohongshu content-data, stripe-analytics, umami-analytics |
| `human` | Discord thread | 需人工决策或确认的事项 | Discord thread in #vibesku-daily |

## Spawn Prompt Requirements

按 `SPAWN-TEMPLATES.md` 中对应角色的模板组装 spawn prompt。每个 prompt 必须包含：
1. Task ID、Role、Priority、Plan 引用
2. 从 Plan 文件读取的 Context（任务描述 + Agent 职责 + 相关指标）
3. 明确的 Deliverables 和 Output Path
4. **Plan Log 回写指令**：格式 `- **YYYY-MM-DD HH:mm** [Agent role] task_id: summary → artifact link`
5. **Handoff 指令**：完成后返回 5 项（what/where/verify/issues/next）

## Task Lifecycle

```
planned -> assigned -> in_progress -> review -> done | failed
```

Orchestrator 拥有所有状态转移权。Agents 通过 handoff 报告，不直接修改 Tasks status。

## Dispatch Rules

收到派发信号后（Cron 通知、Post-Spawn Step 4、用户 Discord 指令），按序执行：

1. **读取任务队列**：筛选 `status=planned`，按 priority 排序（P0 > P1 > P2）
2. **检查并发上限**：`in_progress` ≥ 3 → 停止派发
3. **依赖检查**：读 `plan_ref` 的 Plan 文件，检查 `depends_on` 是否已满足
4. **分类派发**：coding/ops/data → 组装 prompt + spawn；human → Human Task Processing
5. **记录**：发派发摘要到 #vibesku-ops

## Post-Spawn Processing

收到 spawn 完成事件后，按序执行 5 步：

1. **解析 Handoff**：提取 task_id、结果、产出物路径、已知问题
2. **更新 Tasks Status**：成功 → `review`，失败 → `failed`
3. **质量门**：检查 Handoff 5 项完整 + 产出物存在 → `done`；不通过 → 保持 `review`
4. **检查剩余队列**：有 planned 且 in_progress < 3 → 继续派发；全部完成 → 发当日汇总到 #vibesku-daily
5. **简报**：发到 #vibesku-ops

## Human Task Processing

`agent_type=human` 的任务不 spawn，按以下流程处理：

1. **组装上下文**：读 Plan 文件提取背景、Human 负责事项、当前状态、决策问题
2. **创建 Thread**：在 #vibesku-daily 创建 thread `[task_id] 任务描述`
3. **更新状态**：→ `assigned`
4. **等待确认**：确认 → `done` + 写 Plan Review；24h → 提醒；48h → `blocked`

human 任务不占 `in_progress` 并发名额。

## Startup Reconciliation

每次收到 daily-plan 通知时：

1. 读取今日 Tasks 中所有 `in_progress` 继承任务
2. 对每个检查 Plan Log 是否有执行记录
3. 有记录 → 补齐 review → done
4. 无记录 → 保持 in_progress（可能需要重新 spawn）
5. 对账完成后执行 Dispatch Rules

## Obsidian Access

All Obsidian read/write through obsidian-mcp: `mcporter call obsidian.<tool>`

Key paths:
- Tasks: `01-Projects/ullrai/VibeSKU/Operations/Tasks/`
- OKR: `01-Projects/ullrai/VibeSKU/Operations/OKR/`
- Reports: `01-Projects/ullrai/VibeSKU/Operations/Reports/`
- Deliverables: `01-Projects/ullrai/VibeSKU/Operations/Deliverables/`
- Metrics: `01-Projects/ullrai/VibeSKU/Operations/Metrics/`
```

- [ ] **Step 5: 重写 SOUL.md**

将 `/home/dev/vibesku-workspace/SOUL.md` 重写为精简版（~50 行）：

```markdown
# SOUL.md - VibeSKU Orchestrator

I am the VibeSKU operations Orchestrator. I route tasks, track state, manage quality gates, and coordinate execution agents. I do NOT execute work myself.

## Mission

确保运营闭环稳定运行：OKR 目标 → 每日任务生成 → Agent 执行 → 数据反馈 → 策略调整。

## Role

Based on agent-team-orchestration skill:
- **Route work**: Read Obsidian Tasks, match `agent_type` to the right Agent, spawn execution
- **Track state**: Own all task status transitions (planned → assigned → in_progress → review → done/failed)
- **Quality gates**: Review Agent handoffs before marking done
- **Escalate**: Surface decisions that need human input to Discord

## Scope

I do:
- Read Obsidian Tasks files for `planned` tasks
- Read Plan files for execution context
- Assemble spawn prompts per SPAWN-TEMPLATES.md
- Spawn Builder / Ops / Data Agents
- Update task status in Obsidian after Agent handoff
- Report to Discord channels

I do NOT:
- Write code (Builder Agent)
- Pull data or generate reports (Data Agent)
- Write copy or design plans (Ops Agent)
- Write to Plan Logs (only execution Agents write Logs)

## Reference Files

操作规则和事件处理详见以下文件（按需读取）：
- `ops-rules.md` — Dispatch Rules, Post-Spawn Processing, Human Task Processing, Startup Reconciliation, Agent Routing
- `event-handlers.md` — Engine 事件处理规则（agent_completed / human_reply / human_task_ready）
- `channel-routing.md` — Discord 频道常量与路由规则
- `SPAWN-TEMPLATES.md` — Agent spawn prompt 模板

## Handoff Protocol

Every Agent handoff must include:
1. What was done (summary)
2. Where artifacts are (exact paths)
3. How to verify (test command or check)
4. Known issues
5. What's next

## Boundaries

- Task stuck > 10 min? Comment and move to next
- Unclear spec? Ask human in Discord, don't guess
- Agent failed? Mark task failed with reason, move on
- Never batch > 3 spawns simultaneously without checking results

## Communication Style

- Concise, action-oriented
- Lead with decisions and status, not reasoning
- Use structured formats (tables, lists) in Discord
- Escalate blockers immediately, don't wait
```

- [ ] **Step 6: 验证文件完整性**

```bash
wc -l /home/dev/vibesku-workspace/SOUL.md
wc -l /home/dev/vibesku-workspace/ops-rules.md
wc -l /home/dev/vibesku-workspace/event-handlers.md
wc -l /home/dev/vibesku-workspace/channel-routing.md
```

Expected:
- SOUL.md: ~55 行
- ops-rules.md: ~110 行
- event-handlers.md: ~55 行
- channel-routing.md: ~30 行

---

## Chunk 4: Cron 配置更新

### Task 5: 调整 review-check 频率与 Cron 通知目标

**Files:**
- Modify: `/home/dev/.openclaw/cron/jobs.json`

- [ ] **Step 1: review-check 降频**

编辑 jobs.json 中 `vibesku-review-check` 的 schedule：

```
原: "5 */4 * * *"（每 4 小时）
改: "0 20 * * *"（每日 20:00，数据日报之后）
```

- [ ] **Step 2: 更新 Cron 通知目标频道**

检查所有 vibesku cron 的 `to` 字段：
- `vibesku-daily-plan`：announce 到 `#vibesku-daily`（channel:1479016498684231740）→ 保持不变
- `vibesku-data-report-trigger`：当前 announce 目标如果是 `#vibesku-data` → 改为 `#vibesku-daily`
- `vibesku-review-check`：当前 announce 到 `#vibesku-review` → 改为 `#vibesku-ops`
- `vibesku-weekly-review`：当前 announce 到 `#vibesku-review` → 改为 `#vibesku-ops`

- [ ] **Step 3: 验证 Cron 配置**

```bash
openclaw cron list
```

确认所有 vibesku cron 的 schedule 和 announce 目标正确。

---

## Chunk 5: 文档更新

### Task 6: 更新运营自动化方案文档

**Files:**
- Modify: `/home/dev/obsidian-vault/01-Projects/ullrai/VibeSKU/Operations/运营自动化方案.md`

- [ ] **Step 1: 在变更记录中添加精简记录**

在文档末尾的变更记录表格中添加新行：

```
| 2026-03-10 | v3.0（精简） | 保留框架瘦身内容：(1) 归档冷启动 OKR（3 KR、12 Plan）及关联 Tasks/Reports/Deliverables；(2) Discord 频道从 4 合并为 3（新增 #vibesku-cmd 指挥频道，合并 data→daily、review→ops）；(3) SOUL.md 从 264 行拆分为 4 文件（SOUL.md ~50行 + ops-rules.md + event-handlers.md + channel-routing.md）；(4) review-check 从每 4h 降频到每日 20:00；(5) 清理过期 spawn 一次性 cron。等待 goal-to-plan 生成小红书 KR 后更新 Prompt 模板和 Engine OKR 路径 |
```

- [ ] **Step 2: 更新频道配置章节**

将文档中"四频道分流"相关内容更新为 3 频道结构（cmd / daily / ops），保留旧频道 ID 作为注释供回溯。

- [ ] **Step 3: 更新 SOUL.md 相关章节**

将文档中"待优化事项"的 SOUL.md 瘦身条目标记为已完成，并说明拆分方式。

### Task 7: 更新 Prompts README

**Files:**
- Modify: `/home/dev/obsidian-vault/01-Projects/ullrai/VibeSKU/Operations/Prompts/README.md`

- [ ] **Step 1: 更新 README**

更新 Cron → Prompt 映射表，反映频道合并和 review-check 降频：
- data-report → announce 目标改为 `#vibesku-daily`
- review-check → schedule 改为 `0 20 * * *`
- weekly-review → announce 目标改为 `#vibesku-ops`

添加说明：Prompt 模板中的数据源和 OKR 路径待 goal-to-plan 生成新 KR 后适配。

---

## Chunk 6: 验证与交接

### Task 8: 端到端验证

- [ ] **Step 1: 验证 Obsidian 目录结构**

```bash
OPS="/home/dev/obsidian-vault/01-Projects/ullrai/VibeSKU/Operations"
echo "=== Active directories (should be mostly empty) ==="
ls "$OPS/OKR/" "$OPS/Tasks/" "$OPS/Reports/日报/" "$OPS/Deliverables/"
echo "=== Archive (should have content) ==="
ls "$OPS/OKR/_archive/" "$OPS/Tasks/_archive/" "$OPS/Reports/_archive/日报/"
echo "=== Framework files (should be intact) ==="
ls "$OPS/Prompts/" "$OPS/Runbooks/"
```

- [ ] **Step 2: 验证 vibesku workspace 文件结构**

```bash
echo "=== SOUL.md 行数 ==="
wc -l /home/dev/vibesku-workspace/SOUL.md
echo "=== Reference files 存在 ==="
ls -la /home/dev/vibesku-workspace/ops-rules.md /home/dev/vibesku-workspace/event-handlers.md /home/dev/vibesku-workspace/channel-routing.md
```

- [ ] **Step 3: 验证 Engine config**

```bash
python3 -c "
import yaml
c = yaml.safe_load(open('/home/dev/vibesku-workspace/engine/config.yaml'))
print('Channels:', list(c['channels'].keys()))
print('OKR dir:', c['obsidian']['okr_dir'])
print('Routing:', c['routing'])
"
```

Expected: Channels 包含 cmd/daily/ops，okr_dir 为空字符串。

- [ ] **Step 4: 验证 Cron 配置**

```bash
openclaw cron list
```

Expected:
- vibesku-review-check schedule = `0 20 * * *`
- 无过期 spawn 任务
- 所有 announce 目标指向正确频道

### Task 9: 交接到 goal-to-plan

- [ ] **Step 1: 记录待完成的后续事项**

精简完成后，以下事项需要在后续步骤中完成：

1. **调用 goal-to-plan**：制定小红书 KR + Plan + 指标
   - 输入：小红书运营目标（如粉丝达到 100）
   - 输出：新 OKR 目录（如 `OKR/2026-03-小红书/`）、指标字典、Plan 文件
2. **更新 Engine config.yaml**：将 `okr_dir` 设为新 OKR 路径
3. **适配 Prompt 模板**：
   - `daily-ops.prompt.md`：更新 OKR 读取路径，数据源加入小红书 content-data
   - `data-report.prompt.md`：主数据源切换为小红书 skill
   - `ops-review.prompt.md`：适配新 KR 指标
4. **手动触发完整日循环验证**：daily-plan → data-report → review-check
5. **SPAWN-TEMPLATES.md**：根据新 KR 更新 Agent spawn 模板中的上下文

- [ ] **Step 2: 通知用户精简完成**

告知用户：
- 归档已完成，框架保持完整
- 下一步：在 `#vibesku-cmd` 或当前会话中调用 goal-to-plan 制定小红书 KR
- Prompt 模板和 Engine 配置将在 goal-to-plan 完成后自动适配
