> 状态：草稿
> 校验状态：待校验
> schema_version: 0.0.2
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
- **不包含**：占领后掠夺与经营 gate 细则（sy-34 待补）；贸易价表（sy-28）、关系对话脚本（sy-27）。

## 主控制态：`city_control_state`

同一城市实例（或占格城区归属的外部城壳）**同一时刻仅一种**主控制态；判定优先级（高 → 低）：

**效忠** > **未效忠** > **占领** > **未招募 / 已脱离**

| 枚举值 | 中文 | 条件摘要 | AI 行动阶段 |
|--------|------|----------|-------------|
| `ExternalNeutral` | 外部 · 未招募 | 外部城，玩家未招募该城领袖 | **执行** |
| `RecruitedUnloyal` | 招募 · 未效忠 | 招募成功，未激活效忠 | **不执行**（玩家指挥） |
| `RecruitedLoyal` | 招募 · 效忠 | 效忠已激活；外部城实体**消解**，城区划入玩家资产 | **不执行** |
| `Detached` | 已脱离 | 未效忠期 **R ≤ −50**，关系结算后强制脱离 | **执行** |
| `Occupied` | 占领 | **敌对**（**R ≤ −50**）；目标城经交战**打为废墟**后玩家**队伍占格**写入（占格细则 **待定**）；与招募轨**互斥** | **待定**（sy-34） |
| `Takeover` | 接管 | 占格**无活跃人口**；**不是**占领 | **待定**（sy-34） |

**玩家移动城市**不占用上表枚举：程序以 `owner_kind=player_mobile_city` 标识，能力默认 **allow**，仅受 [移动城市专属能力](../../02-系统设计/05-城市与领袖/势力系统.md#移动城市专属能力已定) 与正交修饰 `mobile_city_mode` 约束。

### 效忠后的实例归属

`RecruitedLoyal` 写入后，原外部城**不再**作为独立经营实体存在（见 [效忠 · 城市消解](../../02-系统设计/05-城市与领袖/领袖与势力.md#效忠城市消解与人口留存已定)）。相关城区转为玩家资产，后续 gate 按**玩家移动城市**规则求值；`city_control_state` 在城区实例上可记为 `player_asset`（程序字段 **待定**）或不再挂载外部城态。

## 正交修饰（与主控制态叠加）

下列修饰**不**替代主控制态；在矩阵标为 **allow** 的入口上，修饰可改为 **deny** 或 **conditional**。

| 修饰 ID | 适用对象 | 影响摘要 |
|---------|----------|----------|
| `is_ruin` | 任意城区 | 禁工作区、**不可迁入**；**设施**与**特殊城区能力**失能（见 [废墟失能](../../02-系统设计/03-图层与地点/建筑层/城区总览.md#废墟失能)）；废墟「仅可迁出」与招募未效忠「禁止迁出」冲突时 → **招募未效忠优先**（D-059-06） |
| `hostile_ruin_occupation_ready` | 外部城壳 | **敌对**且满足废墟占领前置（至少一座城区 `is_ruin`；是否须整城全废墟 **待定**）时，**队伍占格**可触发 `Occupied` 写入（sy-34） |
| `topology_connected_to_player` | 未效忠外部城 | 仅影响**粮食**周总结扣减路径（玩家池优先 → 封存回退）；**不是**连接指令（D-059-02） |
| `mobile_city_mode=docked` | **仅**玩家移动城市 | 允许连接 / 分离 / 迁移城区（停泊）；禁整城航行移动 |
| `mobile_city_mode=sailing` | **仅**玩家移动城市 | 允许航行移动；禁连接 / 分离 / 迁移城区 / **城区与设施修复**；队伍进出城受限（sy-19） |
| `relationship_pending_detach` | 未效忠 | 本回合 **R ≤ −50** 但关系结算**尚未**执行：当回合仍 **allow** 合法操作；**下回合**起 `Detached`（D-059-07） |

**外部城永真修饰**：`is_external_city=true` → 永禁连接 / 分离 / 迁移城区 / 停泊航行 / 航行放弃城区（[移动城市专属能力](../../02-系统设计/05-城市与领袖/势力系统.md#移动城市专属能力已定)）。

## 能力入口 ID 与矩阵

图例：**✓** = allow · **✗** = deny · **△** = conditional（见脚注）

### 拓扑

| 入口 ID | 说明 | ExternalNeutral | RecruitedUnloyal | RecruitedLoyal | Detached | Occupied | Takeover | 玩家移动城 |
|---------|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `topo.connect` | 主动连接玩家城 | ✗ | ✗ | — | ✗ | △ | △ | △¹ |
| `topo.separate` | 分离城区 | ✗ | ✗ | — | ✗ | △ | △ | △¹ |
| `topo.reconnect` | 再连接 | ✗ | ✗ | — | ✗ | △ | △ | △¹ |
| `topo.district_relocate` | 迁移城区 | ✗ | ✗ | — | ✗ | ✗ | ✗ | △¹ |

¹ 仅 `mobile_city_mode=docked` 为 **△→✓**；`sailing` 为 **✗**。

### 结构

| 入口 ID | 说明 | ExternalNeutral | RecruitedUnloyal | RecruitedLoyal | Detached | Occupied | Takeover |
|---------|------|:---:|:---:|:---:|:---:|:---:|:---:|
| `struct.repair` | 修复城区结构 | △² | ✓ | ✓³ | △² | △ | △ |
| `struct.dismantle` | 拆解结构回收 | △² | ✓ | ✓³ | △² | △ | △ |
| `struct.transform` | 改造城区（改词条等） | ✗ | ✗ | ✓³ | ✗ | △ | △ |

² 未招募时由 **AI** 决策，玩家 **✗**。³ 效忠后城区归玩家资产，按玩家城 **✓**。¹¹ 玩家移动城 **`mobile_city_mode=sailing`** → **`struct.repair` / `fac.repair` ✗**（须 **停泊**）；见 [分离与拆解 · 修复城区](../../02-系统设计/03-图层与地点/建筑层/分离与拆解.md#修复城区)。

### 人口

| 入口 ID | 说明 | ExternalNeutral | RecruitedUnloyal | RecruitedLoyal | Detached | Occupied | Takeover |
|---------|------|:---:|:---:|:---:|:---:|:---:|:---:|
| `pop.squad_form` | 编组 / 解散 / 补员 | △² | ✓ | ✓³ | △² | △ | ✗ |
| `pop.district_work` | 城区工作分配 | △² | ✓ | ✓³ | △² | △ | △ |
| `pop.work_zone_toggle` | 工作区启闭（**仅特殊城区**模块；**一般城区**走设施行） | △² | ✓⁴ | ✓³ | △² | △ | △ |
| `pop.affiliation_convert` | 人口归属转化 | ✗ | ✗ | ✓³ | ✗ | △ | △ |
| `pop.residential_move_out` | 从住宅迁出 / 改换安置 | △² | ✗ | ✓³ | △² | △ | △ |
| `pop.residential_move_in` | 迁入新居民 | △² | ✓⁵ | ✓³ | △² | △ | △ |

⁴ 废墟 `is_ruin` → 模块工作区 **✗**。⁴ᵇ **`is_core_district`** → 模块工作区**不可关闭**。⁴ᶜ **一般城区**：无 `pop.work_zone_toggle`；各设施 `fac.work_zone_toggle`（与模块**同逻辑**）**待定**字段名。⁵ 废墟 **✗**（不可迁入）；未效忠 **禁止迁出** 优先于废墟「仅可迁出」（D-059-06）。

**编组细则**（各态均为 **allow** 时仍须满足）：[人口预占用](../../02-系统设计/04-资源与人口/人口与迁移.md#编组--人口预占用已定)、[创队与补员](../../02-系统设计/06-单位与交战/队伍系统.md#创队与补员已定)、[单一人口类型](../../02-系统设计/04-资源与人口/人口与迁移.md#编组--单一人口类型已定)、[人口归属](../../02-系统设计/04-资源与人口/人口与迁移.md#人口归属)（D-059-08）。

### 资源

| 入口 ID | 说明 | ExternalNeutral | RecruitedUnloyal | RecruitedLoyal | Detached | Occupied | Takeover |
|---------|------|:---:|:---:|:---:|:---:|:---:|:---:|
| `res.command_consume` | 指令附带非粮食消耗（走玩家池） | ✗ | ✓ | ✓³ | ✗ | △ | △ |
| `res.sealed_draw` | 玩家主动动用封存资源 | ✗ | ✗ | ✓³ | ✗ | △ | △ |
| `res.weekly_food_auto` | 周总结粮食自动扣减 | △² | ✓⁶ | ✓³ | △² | △ | △ |
| `res.cms_storage` | 城市管理系统 · 资源存储分配 | ✗ | ✗ | ✓³ | ✗ | △ | △ |
| `res.manual_transfer` | 手动调拨 / 出库 / 入库 | ✗ | ✗ | ✓³ | ✗ | △ | △ |

⁶ 玩家相连池优先 → 封存粮食回退；**禁止**玩家手动操作（D-059-02）。

### 设施

| 入口 ID | 说明 | ExternalNeutral | RecruitedUnloyal | RecruitedLoyal | Detached | Occupied | Takeover |
|---------|------|:---:|:---:|:---:|:---:|:---:|:---:|
| `fac.build` | 新建造设施 | △² | ✗ | ✓³ | △² | △ | △ |
| `fac.demolish` | 拆除设施 | △² | ✗ | ✓³ | △² | △ | △ |
| `fac.repair` | 修复设施 | △² | ✓ | ✓³ | △² | △ | △ |
| `fac.upgrade` | 升级设施 | △² | ✓ | ✓³ | △² | △ | △ |
| `fac.maintain` | 运维既有设施 | △² | ✓ | ✓³ | △² | △ | △ |

未效忠设施消耗走**玩家资源池**（D-059-04）。¹⁰ 废墟 `is_ruin` → **fac.repair / fac.upgrade / fac.maintain** **✗**（设施侧失能）；**struct.repair**（城区结构）仍按矩阵列（见 T-10）。

### 管理 UI

| 入口 ID | 说明 | ExternalNeutral | RecruitedUnloyal | RecruitedLoyal | Detached | Occupied | Takeover |
|---------|------|:---:|:---:|:---:|:---:|:---:|:---:|
| `ui.cms_open` | 打开城市管理系统 | ✗ | ✓ | ✓³ | ✗ | △ | △ |
| `ui.cms_tab_storage` | 资源存储 Tab 可编辑 | ✗ | ✗ | ✓³ | ✗ | △ | △ |
| `ui.cms_tab_housing` | 人口分配 Tab 迁出可编辑 | ✗ | ✗ | ✓³ | ✗ | △ | △ |
| `ui.cms_tab_workforce` | 人力分配 Tab 可编辑 | ✗ | ✓ | ✓³ | ✗ | △ | △ |

未效忠：**同一面板** + 禁用 + 说明（D-059-01）；效忠 **解除**禁用（D-059-03）。控件级清单见 [城市管理系统 · 招募 · 未效忠 UI](../../02-系统设计/04-资源与人口/城市管理系统.md#招募--未效忠-ui已定)。

### 贸易

| 入口 ID | 说明 | ExternalNeutral | RecruitedUnloyal | RecruitedLoyal | Detached | Occupied | Takeover |
|---------|------|:---:|:---:|:---:|:---:|:---:|:---:|
| `trade.leader_panel` | 领袖页贸易子面板 | △⁷ | ✗ | ✗ | △⁷ | ✗ | △ |
| `trade.caravan_auto` | 商队自动履约 | △⁷ | ✗ | ✗ | △⁷ | ✗ | △ |
| `trade.bypass_dock_wild` | 停泊 / 野外贸易旁路 | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

⁷ 须 **−50 < R < 50** 或 **R ≥ 50**，且**未**招募该领袖（D-059-10）。商队**仅**贸易创建、**不可**手动编组；**己方**商队可指挥（sy-04）。

### 关系

| 入口 ID | 说明 | ExternalNeutral | RecruitedUnloyal | RecruitedLoyal | Detached | Occupied | Takeover |
|---------|------|:---:|:---:|:---:|:---:|:---:|:---:|
| `rel.force_detach` | 关系结算写入强制脱离 | ✗ | △⁸ | ✗ | ✗ | ✗ | ✗ |
| `rel.activate_loyalty` | 关系结算写入效忠 | ✗ | △⁹ | ✗ | ✗ | ✗ | ✗ |
| `rel.ui_forecast` | 关系行动专用 UI 预告 | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

⁸ **R ≤ −50** 且未效忠，环境结算**之后**写入，**下回合** `Detached`（D-059-07）。⁹ **R ≥ 100** 且已招募。关系下降走**剧情 / 脚本对话**警告，**不设**专用 UI（D-059-13）。

### 回合 / AI

| 入口 ID | 说明 | ExternalNeutral | RecruitedUnloyal | RecruitedLoyal | Detached | Occupied | Takeover |
|---------|------|:---:|:---:|:---:|:---:|:---:|:---:|
| `turn.ai_schedule` | AI 行动阶段调度该城 | ✓ | ✗ | ✗ | ✓ | △ | △ |
| `turn.player_command` | 玩家指挥 / 玩家行动 | ✗ | ✓ | ✓³ | ✗ | △ | △ |

招募成功 **下一回合** 起玩家指挥（与关系行动写入时点一致）。

## 求值顺序

```text
1. 解析 owner_kind（external_city | player_mobile_city | occupied_slice）
2. 若 player_mobile_city → 应用 mobile_city_mode 修饰 → 返回
3. 解析主控制态 city_control_state（按优先级链）
4. 查 city_capability_flags 基表 → allow | deny | conditional
5. 叠加 is_ruin、hostile_ruin_occupation_ready、topology_connected_to_player、relationship_pending_detach
6. conditional 行查条件表（关系档位、废墟占领占格、占格人口等）
7. UI 与 API 共用步骤 1～6；禁止 UI 单独放行
```

**组织级关系统计**：己方归属 **4 人降 1** 含 recruited 外部城城区与编组（D-059-12）；与 gate **无关**，但须在关系服务与战斗减员管线统一累计。

## 占领触发（`occupation_trigger` · sy-34 框架）

敌对态将外部城市**打为废墟**后，玩家**队伍占格**写入 `Occupied` 主控制态；与招募 / 效忠**互斥**。程序触发数据雏形如下（占格数量、范围、守军清空 **待定**）。

### 枚举 `occupation_trigger_type`

| 值 | 说明 |
|----|------|
| `ruin_hex_occupation` | **已定**框架：废墟前置 + 队伍占格完成占领 |

### 表：`occupation_trigger_defs`（CSV / SO · 占位）

| 字段 | 类型 | 说明 |
|------|------|------|
| `occupation_trigger_type` | enum | 首版仅 `ruin_hex_occupation` |
| `required_city_ruin_state` | enum | 至少一座城区 `is_ruin=true`；是否须**整城**全废墟 **待定** |
| `occupying_team_id` | string | 触发占格的己方队伍实例 |
| `target_district_id` | string | 占格目标城区（或占格格集合锚点；范围 **待定**） |
| `target_hex_ids` | string[] | 占格格 id 列表（**待定**：`min_hex_count`、是否须清空守军） |
| `home_city_ref` | string | 占领写入前外部城壳 id；写入后控制态 → `Occupied` |
| `home_city_ref_transition` | enum | `external_hostile` → `occupied`（**不**走 `RecruitedUnloyal` / `RecruitedLoyal`） |
| `min_hex_count` | int | **待定**；占格完成所需最少格数 |
| `requires_hostile_relationship` | bool | **true**；须 **R ≤ −50** |
| `mutually_exclusive_with` | enum[] | `RecruitedUnloyal` · `RecruitedLoyal` |

### 占领写入流程（程序顺序 · 已定框架）

1. 校验 **敌对**（**R ≤ −50**）且**未**招募 / **未**效忠目标城领袖。
2. 校验外部城满足 `required_city_ruin_state`（至少一座城区废墟；整城废墟 **待定**）。
3. 校验 `hostile_ruin_occupation_ready` 修饰与队伍占格（`min_hex_count`、守军 **待定**）。
4. 写入 `city_control_state=Occupied`；**不**触发资源封存、招募委托或效忠链。
5. 掠夺范围、占领后指挥 / 经营 / CMS gate **待定**（sy-34）。

设计口径：[废墟占领](../../02-系统设计/05-城市与领袖/领袖与势力.md#废墟占领敌对--已定框架)、[接管 vs 占领](../../02-系统设计/05-城市与领袖/领袖与势力.md#接管-vs-占领已定)。

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
| `Occupied` | enum | 同上 |
| `Takeover` | enum | 同上 |
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
| T-06 | 未效忠 | `RecruitedUnloyal` | 主动连接玩家城 | **deny** |
| T-07 | 未效忠 | `RecruitedUnloyal` | 新建造设施 | **deny**；修复既有 **allow** |
| T-08 | 未效忠 | `RecruitedUnloyal` | 势力城内归属转化 | **deny** |
| T-09 | 废墟 × 未效忠 | `RecruitedUnloyal` + `is_ruin` | 迁出居民 | **deny**（招募优先） |
| T-10 | 废墟 × 未效忠 | `RecruitedUnloyal` + `is_ruin` | 修复城区 | **allow** |
| T-11 | 效忠翻转 | `RecruitedUnloyal` → `RecruitedLoyal` | 打开 CMS 资源 Tab | **allow**；布局不变 |
| T-12 | 脱离 | `Detached` | 玩家打开 CMS | **deny**；AI 恢复调度 |
| T-13 | 占领互斥 | 先 `RecruitedUnloyal` | 触发占领 | **不可**并存；保持招募态 |
| T-14 | 无人口占格 | `Takeover` | 记为占领 | **deny**；应为接管 |
| T-15 | 关系结算前 | `RecruitedUnloyal` + `relationship_pending_detach` | 当回合拆解 | **allow**；下回合脱离 |
| T-16 | 贸易旁路 | `RecruitedUnloyal` | 停泊面对面贸易 | **deny** |
| T-17 | 商队 | `ExternalNeutral`，**R ≥ 0** | 领袖页成交 | 自动编组；**不可**手动建商队 |
| T-18 | 4 人降 1 | `RecruitedUnloyal` | 外部城编组减员 4 人 | 组织级池降 1 关系 |
| T-19 | 补员来源 | `RecruitedUnloyal` | 系统补员 | 相邻格来源池；类型与归属校验 |
| T-20 | 玩家城航行 | `player_mobile` + `sailing` | 迁移城区 | **deny** |
| T-21 | 玩家城停泊 | `player_mobile` + `docked` | 迁移城区 | **allow** |
| T-22 | 未招募 | `ExternalNeutral` | 玩家编组该城队伍 | **deny** |
| T-23 | 废墟失能 | `is_ruin` | 激活城区能力 / 设施运维 | **deny** |
| T-24 | 废墟占领 | `hostile_ruin_occupation_ready` + 队伍占格 | 写入 `Occupied` | **allow**（占格范围 **待定**） |
| T-25 | 占领互斥 | `RecruitedUnloyal` | 敌对废墟占格触发占领 | **deny**；保持招募态 |
| T-26 | 接管非占领 | 占格无活跃人口 | 写入 `Takeover` | **allow**；**不得**记为 `Occupied` |
| T-27 | 废墟失能 × 占领 | `is_ruin` + `Occupied` | 激活设施 / 城区能力 | **deny**（失能优先于占领后修复前） |
| T-28 | 玩家城航行 | `player_mobile` + `sailing` | 修复城区 / 修复设施 | **deny** |
| T-29 | 玩家城停泊 | `player_mobile` + `docked` | 修复城区 | **allow**（仍受废墟 / 招募等矩阵约束） |

## 待实现

- [ ] `city_capability_flag_defs.csv` 落盘并与 SO 导入管线对接
- [ ] `CityCapabilityService` 单元测试覆盖上表 T-01～T-27
- [ ] 占领 / 接管列在 sy-34 闭合后补全 **△** 条件（废墟占领框架 **已定**；掠夺与占领后 gate **待定**）
- [ ] 航行态打开 CMS 是否只读（sy-19 / sy-23 交叉）

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-10 | 0.0.1 | 初稿：D-059-01～13 闭合；主控制态矩阵、正交修饰、UI/API 守卫、测试矩阵与配置雏形 |
| 2026-07-10 | 0.0.2 | 废墟失能修饰；Occupied 改为废墟+占格；`occupation_trigger` 字段雏形；T-23～27 |
