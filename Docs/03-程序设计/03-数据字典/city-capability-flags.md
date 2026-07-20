> 状态：草稿
> 校验状态：待校验
> schema_version: 0.1.0
> 数据层级：L1 实现
> 对应设计文档：[势力系统 · sf-02](../../02-系统设计/05-城市与领袖/势力系统.md#sf-02-能力-gate-已定)、[领袖与势力](../../02-系统设计/05-城市与领袖/领袖与势力.md)、[城市管理系统](../../02-系统设计/04-资源与人口/城市管理系统.md)

← [数据字典](./README.md)

# 城市能力开关：`city_capability_flags`

| 字段 | 内容 |
|------|------|
| 状态 | 草稿 |
| 校验状态 | 待校验 |
| 最后更新 | 2026-07-10 |
| 关联设计 | [势力系统 · sf-02](../../02-系统设计/05-城市与领袖/势力系统.md#sf-02-能力-gate-已定)、[领袖与势力](../../02-系统设计/05-城市与领袖/领袖与势力.md)、[城市管理系统 · 招募 · 未效忠 UI](../../02-系统设计/04-资源与人口/城市管理系统.md#招募--未效忠-ui已定)、[回合与行动表 · 关系结算](../../02-系统设计/07-玩法循环/回合与行动表.md#关系结算顺序) |

## 目标

在「外部城市与玩家移动城市**共用城区运行时**」前提下，用**单一数据源**定义：每种**主控制态**（及正交修饰）下，各**城市层操作 / UI 入口 / 指令类型**为 **allow**、**deny** 或 **conditional**。

- **UI 按钮**、**指令校验**、**AI 模块停写**、**城市管理系统禁用态**须读同一表（或同一求值服务），**禁止**硬编码 `if (isExternal)` 散落判断。
- 策划裁定 **D-059-01～13** 已全部闭合；本文档为程序落地规格。

## 范围

- **包含**：`city_control_state` 主枚举、正交修饰、能力入口 ID、状态 × 入口矩阵、求值顺序、[占领触发](#占领触发occupation_trigger--sy-34-框架)占位、UI/API 守卫约定、验收测试矩阵、配置 SO / CSV 字段雏形。
- **不包含**：沦陷后经营细则（沦陷不参与经营 gate，已定）；接管规则（已定）；贸易价表（sy-28）、关系对话脚本（sy-27）。

## 主控制态：`city_control_state`

同一城市实例（或占格城区归属的外部城壳）**同一时刻仅一种**主控制态；判定优先级（高 → 低）：

**效忠** > **未效忠** > **占领** > **未招募 / 已脱离**

| 枚举值 | 中文 | 条件摘要 | AI 行动阶段 |
|--------|------|----------|-------------|
| `ExternalNeutral` | 外部 · 未招募 | 外部城，玩家未招募该城领袖 | **执行** |
| `RecruitedUnloyal` | 招募 · 未效忠 | 招募成功，未激活效忠 | **不执行**（玩家指挥） |
| `RecruitedLoyal` | 招募 · 效忠 | 效忠已激活；外部城实体**消解**，城区划入玩家资产 | **不执行** |
| `Detached` | 已脱离 | 未效忠期 **R ≤ −50**，关系结算后强制脱离 | **执行** |
| `Surrendered` | 沦陷 | 领袖所在城区被占领 → 守军不主动还击；玩家可安全逐城区占领。一切具体操作由占领 → 接管链路负责，沦陷不参与经营 gate | **守军不主动还击**（AI 仍执行非战斗调度） |

**已废止 `Takeover` 枚举**（sy-34 分项⑪ 已定）：接管是**城区级工作**（`takeover_district`），不占城市控制态。接管完成后城区写 `district_ownership=player`，**视为玩家直接资产**——资源与经营 gate 按玩家城区规则求值（同效忠划归城区）；人口归属不随之转移。

**玩家移动城市**不占用上表枚举：程序以 `owner_kind=player_mobile_city` 标识，能力默认 **allow**，仅受 [移动城市专属能力](../../02-系统设计/05-城市与领袖/势力系统.md#移动城市专属能力已定) 与正交修饰 `mobile_city_mode` 约束。

### 效忠后的实例归属

`RecruitedLoyal` 写入后，原外部城**不再**作为独立经营实体存在（见 [效忠 · 城市消解](../../02-系统设计/05-城市与领袖/领袖与势力.md#效忠城市消解与人口留存已定)）。相关城区转为玩家资产，后续 gate 按**玩家移动城市**规则求值；`city_control_state` 在城区实例上可记为 `player_asset`（程序字段 **待定**）或不再挂载外部城态。**接管**（`takeover_district`）完成后的城区同理——按玩家资产求值，不再参与外部城 gate。

## 正交修饰（与主控制态叠加）

下列修饰**不**替代主控制态；在矩阵标为 **allow** 的入口上，修饰可改为 **deny** 或 **conditional**。

| 修饰 ID | 适用对象 | 影响摘要 |
|---------|----------|----------|
| `is_ruin` | 任意城区 | 禁工作区、**不可迁入**；**设施**与**特殊城区能力**失能（见 [废墟失能](../../02-系统设计/03-图层与地点/建筑层/城区总览.md#废墟失能)）；废墟「仅可迁出」与招募未效忠「禁止迁出」冲突时 → **招募未效忠优先**（D-059-06） |
| `leader_district_claimed` | 外部城壳 | 敌对（**R ≤ −50**）且领袖所在城区被「宣称占领」工作完成后 → 城市进入**沦陷**（`Surrendered`）（sy-34 已定） |
| `topology_connected_to_player` | 未效忠外部城 | 仅影响**粮食**周总结扣减路径（玩家池优先 → 封存回退）；**不是**连接指令（D-059-02） |
| `mobile_city_mode=docked` | **仅**玩家移动城市 | 允许连接 / 分离 / 迁移城区（停泊）；禁整城航行移动 |
| `mobile_city_mode=sailing` | **仅**玩家移动城市 | 允许航行移动；禁连接 / 分离 / 迁移城区 / **城区与设施修复**；队伍进出城受限（sy-19） |
| `relationship_pending_detach` | 未效忠 | 本回合 **R ≤ −50** 但关系结算**尚未**执行：当回合仍 **allow** 合法操作；**下回合**起 `Detached`（D-059-07） |

**外部城永真修饰**：`is_external_city=true` → 永禁连接 / 分离 / 迁移城区 / 停泊航行 / 航行放弃城区（[移动城市专属能力](../../02-系统设计/05-城市与领袖/势力系统.md#移动城市专属能力已定)）。

## 能力入口 ID 与矩阵

图例：**✓** = allow · **✗** = deny · **△** = conditional（见脚注）

**沦陷列口径**（sy-34 分项⑨ 已定）：沦陷**不参与经营 gate**——玩家操作入口一律 **✗**，一切具体操作走占领（中立城区）→ 接管（玩家资产）链路；例外仅 `turn.ai_schedule`（AI 仍执行非战斗调度，守军不主动还击）。**接管后城区不在下表**——`district_ownership=player`，按玩家城区规则求值。

### 拓扑

| 入口 ID | 说明 | ExternalNeutral | RecruitedUnloyal | RecruitedLoyal | Detached | Surrendered | 玩家移动城 |
|---------|------|:---:|:---:|:---:|:---:|:---:|:---:|
| `topo.connect` | 主动连接玩家城 | ✗ | ✓ | — | ✗ | ✗ | △¹ |
| `topo.separate` | 分离城区 | ✗ | ✓ | — | ✗ | ✗ | △¹ |
| `topo.reconnect` | 再连接 | ✗ | ✓ | — | ✗ | ✗ | △¹ |
| `topo.district_relocate` | 迁移城区 | ✗ | ✗ | — | ✗ | ✗ | △¹ |

¹ 仅 `mobile_city_mode=docked` 为 **△→✓**；`sailing` 为 **✗**。

### 结构

| 入口 ID | 说明 | ExternalNeutral | RecruitedUnloyal | RecruitedLoyal | Detached | Surrendered |
|---------|------|:---:|:---:|:---:|:---:|:---:|
| `struct.repair` | 修复城区结构 | △² | ✓ | ✓³ | △² | ✗ |
| `struct.dismantle` | 拆解结构回收 | △² | ✗ | ✓³ | △² | ✗ |
| `struct.transform` | 改造城区（改词条等） | ✗ | ✗ | ✓³ | ✗ | ✗ |

² 未招募时由 **AI** 决策，玩家 **✗**。³ 效忠后城区归玩家资产，按玩家城 **✓**。¹¹ 玩家移动城 **`mobile_city_mode=sailing`** → **`struct.repair` / `fac.repair` ✗**（须 **停泊**）；见 [分离与拆解 · 修复城区](../../02-系统设计/03-图层与地点/建筑层/分离与拆解.md#修复城区)。

### 人口

| 入口 ID | 说明 | ExternalNeutral | RecruitedUnloyal | RecruitedLoyal | Detached | Surrendered |
|---------|------|:---:|:---:|:---:|:---:|:---:|
| `pop.squad_form` | 编组 / 解散 / 补员 | △² | ✓ | ✓³ | △² | ✗ |
| `pop.district_work` | 城区工作分配 | △² | ✓ | ✓³ | △² | ✗ |
| `pop.work_zone_toggle` | 工作区启闭（**仅特殊城区**模块；**一般城区**走设施行） | △² | ✓⁴ | ✓³ | △² | ✗ |
| `pop.affiliation_convert` | 人口归属转化 | ✗ | ✗ | ✓³ | ✗ | ✗ |
| `pop.residential_move_out` | 从住宅迁出 / 改换安置 | △² | ✗ | ✓³ | △² | ✗ |
| `pop.residential_move_in` | 迁入新居民 | △² | ✗⁵ | ✓³ | △² | ✗ |

⁴ 废墟 `is_ruin` → 模块工作区 **✗**。⁴ᵇ **`is_core_district`** → 模块工作区**不可关闭**。⁴ᶜ **一般城区**：无 `pop.work_zone_toggle`；各设施 `fac.work_zone_toggle`（与模块**同逻辑**）**待定**字段名。⁵ 废墟 **✗**（不可迁入）；未效忠**不可迁入**（人口锁定在原城市）；迁出见 `pop.residential_move_out` 行。

**编组细则**（各态均为 **allow** 时仍须满足）：[人口预占用](../../02-系统设计/04-资源与人口/人口与迁移.md#编组--人口预占用已定)、[创队与补员](../../02-系统设计/06-单位与交战/队伍系统.md#创队与补员已定)、[单一人口类型](../../02-系统设计/04-资源与人口/人口与迁移.md#编组--单一人口类型已定)、[人口归属](../../02-系统设计/04-资源与人口/人口与迁移.md#人口归属)（D-059-08）。**废墟**与**中立城区**（`district_ownership=neutral`）均**不可**编组——仅玩家归属城区可编组。

**人口归属转化方向**：`pop.affiliation_convert` 指**以该城区人口为原料**转化为玩家持有领袖对应的人口归属；**不是**将其他人口转化为该城区当前人口的类型。中立城区 / 沦陷城区人口是转化的**原材料**，需要玩家持有目标归属对应的领袖方可完成转化。

### 资源

| 入口 ID | 说明 | ExternalNeutral | RecruitedUnloyal | RecruitedLoyal | Detached | Surrendered |
|---------|------|:---:|:---:|:---:|:---:|:---:|
| `res.command_consume` | 指令附带非粮食消耗（走玩家池） | ✗ | ✓ | ✓³ | ✗ | ✗ |
| `res.sealed_draw` | 玩家主动动用封存资源 | ✗ | ✗ | ✓³ | ✗ | ✗ |
| `res.weekly_food_auto` | 周总结粮食自动扣减 | △² | ✓⁶ | ✓³ | △² | ✗ |
| `res.cms_storage` | 城市管理系统 · 资源存储分配 | ✗ | ✗ | ✓³ | ✗ | ✗ |
| `res.manual_transfer` | 手动调拨 / 出库 / 入库 | ✗ | ✗ | ✓³ | ✗ | ✗ |

⁶ 玩家相连池优先 → 封存粮食回退；**禁止**玩家手动操作（D-059-02）。

### 设施

| 入口 ID | 说明 | ExternalNeutral | RecruitedUnloyal | RecruitedLoyal | Detached | Surrendered |
|---------|------|:---:|:---:|:---:|:---:|:---:|
| `fac.build` | 新建造设施 | △² | ✗ | ✓³ | △² | ✗ |
| `fac.demolish` | 拆除设施 | △² | ✗ | ✓³ | △² | ✗ |
| `fac.repair` | 修复设施 | △² | ✓ | ✓³ | △² | ✗ |
| `fac.upgrade` | 升级设施 | △² | ✓ | ✓³ | △² | ✗ |
| `fac.maintain` | 运维既有设施 | △² | ✓ | ✓³ | △² | ✗ |

未效忠设施消耗走**玩家资源池**（D-059-04）。¹⁰ 废墟 `is_ruin` → **fac.repair / fac.upgrade / fac.maintain** **✗**（设施侧失能）；**struct.repair**（城区结构）仍按矩阵列（见 T-10）。

### 管理 UI

| 入口 ID | 说明 | ExternalNeutral | RecruitedUnloyal | RecruitedLoyal | Detached | Surrendered |
|---------|------|:---:|:---:|:---:|:---:|:---:|
| `ui.cms_open` | 打开城市管理系统 | ✗ | ✓ | ✓³ | ✗ | ✗ |
| `ui.cms_tab_storage` | 资源存储 Tab 可编辑 | ✗ | ✗ | ✓³ | ✗ | ✗ |
| `ui.cms_tab_housing` | 人口分配 Tab 迁出可编辑 | ✗ | ✗ | ✓³ | ✗ | ✗ |
| `ui.cms_tab_workforce` | 人力分配 Tab 可编辑 | ✗ | ✓ | ✓³ | ✗ | ✗ |

未效忠：**同一面板** + 禁用 + 说明（D-059-01）；效忠 **解除**禁用（D-059-03）。控件级清单见 [城市管理系统 · 招募 · 未效忠 UI](../../02-系统设计/04-资源与人口/城市管理系统.md#招募--未效忠-ui已定)。

### 贸易

| 入口 ID | 说明 | ExternalNeutral | RecruitedUnloyal | RecruitedLoyal | Detached | Surrendered |
|---------|------|:---:|:---:|:---:|:---:|:---:|
| `trade.leader_panel` | 领袖页贸易子面板 | △⁷ | ✗ | ✗ | △⁷ | ✗ |
| `trade.caravan_auto` | 商队自动履约 | △⁷ | ✗ | ✗ | △⁷ | ✗ |
| `trade.bypass_dock_wild` | 停泊 / 野外贸易旁路 | ✗ | ✗ | ✗ | ✗ | ✗ |

⁷ 须 **−50 < R < 50** 或 **R ≥ 50**，且**未**招募该领袖（D-059-10）。商队**仅**贸易创建、**不可**手动编组；**己方**商队可指挥（sy-04）。

### 关系

| 入口 ID | 说明 | ExternalNeutral | RecruitedUnloyal | RecruitedLoyal | Detached | Surrendered |
|---------|------|:---:|:---:|:---:|:---:|:---:|
| `rel.force_detach` | 关系结算写入强制脱离 | ✗ | △⁸ | ✗ | ✗ | ✗ |
| `rel.activate_loyalty` | 关系结算写入效忠 | ✗ | △⁹ | ✗ | ✗ | ✗ |
| `rel.ui_forecast` | 关系行动专用 UI 预告 | ✗ | ✗ | ✗ | ✗ | ✗ |

⁸ **R ≤ −50** 且未效忠，环境结算**之后**写入，**下回合** `Detached`（D-059-07）。⁹ **R ≥ 100** 且已招募。关系下降走**剧情 / 脚本对话**警告，**不设**专用 UI（D-059-13）。

### 回合 / AI

| 入口 ID | 说明 | ExternalNeutral | RecruitedUnloyal | RecruitedLoyal | Detached | Surrendered |
|---------|------|:---:|:---:|:---:|:---:|:---:|
| `turn.ai_schedule` | AI 行动阶段调度该城 | ✓ | ✗ | ✗ | ✓ | △¹² |
| `turn.player_command` | 玩家指挥 / 玩家行动 | ✗ | ✓ | ✓³ | ✗ | ✗ |

招募成功 **下一回合** 起玩家指挥（与关系行动写入时点一致）。¹² 沦陷城市 AI **仅执行非战斗调度**——守军不主动还击（受攻击仍可反击）。

## 中立城区权限子表

无归属城区（`district_ownership=neutral`，即 `faction=null, city=null`）**不占城市控制态枚举**——它没有所属城市，因此单独以子表表达操作权限。子表仅列与主矩阵默认 `deny` 有差异的入口；未列入的入口一律 `deny`。

| 入口 ID | 中文说明 | 中立城区 | 说明 |
|---------|----------|:--:|------|
| `struct.dismantle` | 拆解结构回收金属 | ✓ | |
| `struct.repair` | 修复城区结构 | ✓ | |
| `res.cms_storage` | 城市管理系统 · 资源存储分配 | ✓ | |
| `res.manual_transfer` | 手动调拨 / 出库 / 入库 | ✓ | |
| `pop.residential_move_out` | 人口迁出 | ✓ | |
| `pop.residential_move_in` | 人口迁入 | ✓ | |

其余入口均为 `deny`：

- **`topo.*`（链接/分离/迁移城区）**：不可——无归属城区未接入玩家城市拓扑。
- **`fac.*`（设施新建/拆除/修复/升级/运维）**：不可——需归属权。
- **`pop.squad_form` / `pop.district_work` / `pop.work_zone_toggle`**（编组/工作分配/工作区开关）：不可——无归属城区人口不归玩家调用，工作需玩家执行`队伍级任务`而非占用本地人口。
- **`struct.transform`**（改造城区/改词条）：不可——同设施，需归属权。

**正交修饰**：`is_ruin`（是否废墟）叠加于子表结果之上——子表返回 `allow` 的入口，若 `is_ruin=true` 则降为 `deny`（废墟时拆解/修复/存取资源仍可执行，但人口迁入不可）。

## 求值顺序

```text
1. 解析 owner_kind（external_city | player_mobile_city | district_neutral | district_player）
2. 若 player_mobile_city → 应用 mobile_city_mode 修饰 → 返回
3. 若 district_neutral（无归属城区，`district_ownership=neutral`）
   → 查「中立城区权限子表」→ allow / deny
   → 叠加 is_ruin 修饰（子表 allow 但 is_ruin=true → deny，毁时人口迁入/设施入口禁用）
   → 返回
4. 若 district_player（接管完成或效忠划归，district_ownership=player）→ 按玩家资产求值（同玩家城区）→ 返回
5. 解析主控制态 city_control_state（按优先级链：效忠 > 未效忠/沦陷 > 未招募/已脱离）
6. 查 city_capability_flags 基表 → allow | deny | conditional
7. 叠加 is_ruin、leader_district_claimed、topology_connected_to_player、relationship_pending_detach
8. conditional 行查条件表（关系档位、中立城区操作、占格人口等）
9. UI 与 API 共用步骤 1～8；禁止 UI 单独放行
```

**组织级关系统计**：己方归属 **4 人降 1** 含 recruited 外部城城区与编组（D-059-12）；与 gate **无关**，但须在关系服务与战斗减员管线统一累计。

## 占领与接管触发（`district_claim_trigger` · sy-34 已定框架）

占领与接管均为城区级工作，处理中立城区的剥离与接收：

- **占领**（`claim_district`）：武装单位完成 → 外部城区脱离原城市变为中立
- **接管**（`takeover_district`）：工程队完成 → 中立城区产权归玩家；人口不随之转移

### 枚举 `district_claim_trigger_type`

| 值 | 说明 |
|----|------|
| `claim_district` | **已定**：武装单位在外部城市城区格完成「宣称占领」→ 城区脱离原城市（中立） |
| `takeover_district` | **已定**：工程队在中立城区格完成「接管」→ 城区结构归属 → 玩家 |

### 表：`district_claim_trigger_defs`（CSV / SO）

| 字段 | 类型 | 说明 |
|------|------|------|
| `trigger_type` | enum | `claim_district` \| `takeover_district` |
| `occupying_team_id` | string | 发起工作的己方队伍实例 |
| `target_district_id` | string | 目标城区 |
| `home_city_ref` | string | 占领前外部城壳 id（仅 `claim_district` 有值） |
| `district_ownership_transition` | enum | `claim_district`：`external_hostile` → `neutral`；`takeover_district`：`neutral` → `player` |
| `is_leader_district` | bool | 仅 `claim_district`——若为领袖所在城区 → 同步触发 `city_control_state=Surrendered` |
| `requires_hostile_relationship` | bool | 仅 `claim_district`：**true**；须 **R ≤ −50** |
| `required_team_ability` | enum | `claim_district`：`combat`（武装）；`takeover_district`：`engineer`（工程） |
| `work_type` | string | **已定**：`claim_district` \| `takeover_district` |
| `base_workload` | int | **已定**：**2**（2 回合） |

### 触发流程（程序顺序 · 已定框架）

**占领（`claim_district`）**：

1. 校验 **R ≤ −50**（敌对）且**未**招募 / **未**效忠目标城领袖。
2. 武装单位在目标城区格上发起「宣称占领」工作。
3. 工作完成：`district_ownership=neutral`（中立无主）。
4. 若 `is_leader_district=true`：`city_control_state=Surrendered`（沦陷）。
5. **不**触发资源封存、招募委托或效忠链。

**接管（`takeover_district`）**：

1. 校验目标城区 `district_ownership=neutral`（中立），且格上无敌对守军。
2. 工程队在场，发起「接管」工作。
3. 工作完成：`district_ownership=player`（城区结构归属 → 玩家）。
4. 人口**不**因接管改变归属——无对应领袖的人口仍不可调用（编组/工作），可迁移与转化。
5. **不**触发招募委托或效忠链。

设计口径：[领袖与势力 · 占领、沦陷与招募](../../02-系统设计/05-城市与领袖/领袖与势力.md#占领沦陷与招募分轨--已定框架)。

## UI / API 统一守卫

| 要求 | 说明 |
|------|------|
| **单一数据源** | `CityCapabilityService.Can(cityRef, entryId)`（名称 **待定**）为 UI 禁用态与 `GameplayAbility` / 指令校验的**唯一**入口 |
| **禁用文案** | UI 从 `deny_reason_template_id` 读取简体中文模板（见 [城市管理系统 · 控件清单](../../02-系统设计/04-资源与人口/城市管理系统.md#招募--未效忠-ui已定)） |
| **只读展示** | `readonly` 控件仍 **打开** Tab，**不**隐藏；与 **deny** 区分 |
| **效忠 diff** | `RecruitedUnloyal → RecruitedLoyal` 仅 **解除**对应 `deny`；**不改**面板布局 |
| **AI 停写** | `turn.ai_schedule=deny` 时 AI 模块**不得**写入该城行动表 |

## 配置形态（程序雏形）

### 枚举 `city_control_state`

见 [tables/shared/enums.csv](./tables/shared/enums.csv)（`city_control_state` 组）。

### 表：`city_capability_flag_defs`（CSV / SO）

| 字段 | 类型 | 说明 |
|------|------|------|
| `entry_id` | string | 如 `pop.residential_move_out` |
| `category` | string | `topo` / `struct` / `pop` / `res` / `fac` / `ui` / `trade` / `rel` / `turn` |
| `display_name_zh` | string | 策划可读名称 |
| `ExternalNeutral` | enum | `allow` / `deny` / `conditional` / `na` |
| `RecruitedUnloyal` | enum | 同上 |
| `RecruitedLoyal` | enum | 同上 |
| `Detached` | enum | 同上 |
| `Surrendered` | enum | 同上 |
| `player_mobile_default` | enum | 玩家移动城默认可用性 |
| `deny_reason_template_id` | string | 可空；UI 禁用说明 |
| `condition_ref` | string | `conditional` 时指向条件脚本或 SO |

### 运行时：`city_instance_state` 扩展字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `city_control_state` | enum | 主控制态 |
| `is_external_city` | bool | 是否外部城壳 |
| `recruited_leader_id` | string | 可空；招募锚定领袖 |
| `loyalty_activated_turn` | int | 可空；效忠写入回合 |
| `topology_connected_to_player` | bool | 周总结扣粮用；拓扑既成 |
| `ai_module_enabled` | bool | 由 `turn.ai_schedule` 派生缓存 |

### SO 类（Unity）

| 类型 | 用途 |
|------|------|
| `CityCapabilityFlagConfigSO` | 单行 `entry_id` + 各态列 |
| `CityCapabilityFlagTableSO` | 聚合全表；Editor 可导 CSV |
| `CityDenyReasonTemplateSO` | `template_id` → 简体中文说明 |

## 验收测试矩阵

| # | 场景 | 主控制态 / 修饰 | 操作 | 期望 |
|---|------|-----------------|------|------|
| T-01 | 未效忠 + 玩家指挥 | `RecruitedUnloyal` | 编组外出 | **allow**；住宅占用不变 |
| T-02 | 未效忠 | `RecruitedUnloyal` | 从住宅迁出 | **deny** |
| T-03 | 未效忠 | `RecruitedUnloyal` | 管理面板手动出库 | **deny** |
| T-04 | 未效忠 + 相连 | `RecruitedUnloyal` + `topology_connected_to_player` | 周总结扣粮 | 玩家池优先；不足走封存 |
| T-05 | 未效忠 + 未相连 | `RecruitedUnloyal` | 周总结扣粮 | 封存回退；玩家池不强制 |
| T-06 | 未效忠 | `RecruitedUnloyal` | 主动连接玩家城 | **allow**；城区可接入玩家移动城市拓扑 |
| T-07 | 未效忠 | `RecruitedUnloyal` | 新建造设施 | **deny**；修复既有 **allow** |
| T-08 | 未效忠 | `RecruitedUnloyal` | 势力城内归属转化 | **deny** |
| T-09 | 废墟 × 未效忠 | `RecruitedUnloyal` + `is_ruin` | 迁出居民 | **deny**（招募优先） |
| T-10 | 废墟 × 未效忠 | `RecruitedUnloyal` + `is_ruin` | 修复城区 | **allow** |
| T-11 | 效忠翻转 | `RecruitedUnloyal` → `RecruitedLoyal` | 打开 CMS 资源 Tab | **allow**；布局不变 |
| T-12 | 脱离 | `Detached` | 玩家打开 CMS | **deny**；AI 恢复调度 |
| T-13 | 沦陷互斥 | 先 `RecruitedUnloyal` | 触发城区占领 | **不可**并存；保持招募态 |
| T-14 | 接管后玩家资产 | `district_ownership=player`（接管完成） | 玩家经营该城区（资源、设施等） | **allow**（按玩家城区规则求值；人口归属不变仍受限） |
| T-15 | 关系结算前 | `RecruitedUnloyal` + `relationship_pending_detach` | 当回合连接城区 | **allow**；下回合脱离 |
| T-16 | 贸易旁路 | `RecruitedUnloyal` | 停泊面对面贸易 | **deny** |
| T-17 | 商队 | `ExternalNeutral`，**R ≥ 0** | 领袖页成交 | 自动编组；**不可**手动建商队 |
| T-18 | 4 人降 1 | `RecruitedUnloyal` | 外部城编组减员 4 人 | 组织级池降 1 关系 |
| T-19 | 补员来源 | `RecruitedUnloyal` | 系统补员 | 相邻格来源池；类型与归属校验 |
| T-20 | 玩家城航行 | `player_mobile` + `sailing` | 迁移城区 | **deny** |
| T-21 | 玩家城停泊 | `player_mobile` + `docked` | 迁移城区 | **allow** |
| T-22 | 未招募 | `ExternalNeutral` | 玩家编组该城队伍 | **deny** |
| T-23 | 废墟失能 | `is_ruin` | 激活城区能力 / 设施运维 | **deny** |
| T-24 | 宣称占领 | 武装单位在城区格完成「宣称占领」工作 | 写入 `district_ownership=neutral` | **allow**；城区变为中立 |
| T-25 | 沦陷触发 | `leader_district_claimed` + `is_leader_district` | 写入 `Surrendered` | **allow**；城市沦陷 |
| T-26 | 接管中立城区 | 工程队在中立城区格完成「接管」工作 | 写入 `district_ownership=player` | **allow**；城区产权归玩家；人口不转移 |
| T-27 | 废墟失能 × 沦陷 | `is_ruin` + `Surrendered` | 激活设施 / 城区能力 | **deny**（失能优先） |
| T-28 | 玩家城航行 | `player_mobile` + `sailing` | 修复城区 / 修复设施 | **deny** |
| T-29 | 玩家城停泊 | `player_mobile` + `docked` | 修复城区 | **allow**（仍受废墟 / 招募等矩阵约束） |
| T-30 | 接管后连接 | `district_ownership=player`（接管完成） | 连接至玩家移动城市 | **allow**（归属权已归玩家；连接需另做拓扑操作） |
| T-31 | 沦陷守军行为 | `Surrendered` | 守军主动攻击玩家单位 | **deny**（沦陷后守军不主动还击） |
| T-32 | 沦陷资源抽取 | `Surrendered` | 玩家直接抽取城市资源 | **不适用**——资源抽取走占领 → 接管链路，沦陷不参与 |

## 待实现

- [ ] `city_capability_flag_defs.csv` 落盘并与 SO 导入管线对接
- [ ] `CityCapabilityService` 单元测试覆盖上表 T-01～T-32
- [x] 航行态打开 CMS 是否只读（sy-19 / sy-23 交叉）：**已定**——航行态仅阻断精密工作，CMS 为静态配置面板，航行中完全可用、不设只读（2026-07-19）。

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-10 | 0.0.1 | 初稿：D-059-01～13 闭合；主控制态矩阵、正交修饰、UI/API 守卫、测试矩阵与配置雏形 |
| 2026-07-10 | 0.0.2 | 废墟失能修饰；Occupied 改为废墟+占格；`occupation_trigger` 字段雏形；T-23～27 |
| 2026-07-16 | 0.0.3 | **sy-34 大幅闭合**：Occupied 替换为 Surrendered（沦陷城市级状态）；占领重定义为城区级工作（`claim_district` work_type）；`hostile_ruin_occupation_ready` 替换为 `leader_district_claimed`；中立城区以 `district_ownership=neutral` 标识并**完全沿用废墟规则**（分项⑧闭合）；沦陷不参与经营 gate（分项⑨闭合，T-31/T-32 更新）；`base_workload` 已定 **2**（宣称占领 / 接管均 2 回合）；新增 T-30～T-32 测试项 |
| 2026-07-16 | 0.1.0 | **sy-34 分项⑪闭合（全部闭合）**：废止 `Takeover` 城市级枚举——接管后城区写 `district_ownership=player`，**视为玩家直接资产**，资源与经营 gate 按玩家城区规则求值；各矩阵移除 Takeover 列；沦陷列按分项⑨对齐（玩家操作入口一律 ✗，仅 `turn.ai_schedule` 保留非战斗调度 △）；求值顺序新增 `district_player` 分支；T-14 更新为接管后玩家资产用例 |
| 2026-07-20 | 0.2.0 | **sy-30 对齐**：新增「中立城区权限子表」节——无归属城区不占城市控制态枚举、以独立子表表达权限（6 个 allow 入口 + 其余 deny）；废止求值顺序第 3 步旧口径「沿用废墟规则」（归属与废墟是正交维度）。主矩阵 `RecruitedUnloyal` 列修正 6 项：`topo.connect/separate/reconnect` ✗→✓（可链接）、`struct.dismantle` ✓→✗（资源不共享）、`pop.residential_move_in` ✓→✗（人口锁定）。测试用例 T-06 更新为 allow、T-15 改用连接操作 |
