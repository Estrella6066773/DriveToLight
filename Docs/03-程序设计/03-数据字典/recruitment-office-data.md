> 状态：草稿
> 校验状态：部分符合
> schema_version: 0.0.2
> 数据层级：L5 实现
> 对应设计文档：[征兵办](../../02-系统设计/04-资源与人口/荒野地点/征兵办.md)、[村镇](../../02-系统设计/04-资源与人口/荒野地点/村镇.md)、[荒野地点 · 资源点与采集设施](../../02-系统设计/04-资源与人口/荒野地点.md#资源点与采集设施)

← [数据字典](./README.md)

# 征兵办数据结构：`recruitment_office`

| 字段 | 内容 |
|------|------|
| 状态 | 草稿 |
| 校验状态 | 部分符合 |
| 最后更新 | 2026-07-11 |
| 关联设计 | [征兵办](../../02-系统设计/04-资源与人口/荒野地点/征兵办.md)、[村镇](../../02-系统设计/04-资源与人口/荒野地点/村镇.md)、[人口与迁移 · 人口归属](../../02-系统设计/04-资源与人口/人口与迁移.md#人口归属)、[城市管理系统 · 人力类型名单占位表](../../02-系统设计/04-资源与人口/城市管理系统.md#人力类型名单占位表占位--待策划定案--sy-23)、[四类资源产出锚](../../02-系统设计/04-资源与人口/四种核心资源.md#四类资源产出锚已定) |

## 目标

为 **村镇** 格上的 **[征兵办](../../02-系统设计/04-资源与人口/荒野地点/征兵办.md)** 提供程序数据雏形：储量人口提取、工作结算、提取后人口归属写入。**不包含**贸易、领袖页或商队逻辑（村镇 **已定** 无此类入口）。

## 范围

- **包含**：村镇储量运行时、`recruitment_office` 设施实例字段、`extract_reserve` 工作结算写入、提取后 `population_type_id` 占位映射；**首版产出 / 建造数值**（见下）。
- **不包含**：住房校验失败反馈细则（sy-14）、`FacilityProductionService` 自动产出路径（征兵办 **不走**该路径，见 [设施数据结构 · 人口归属转化](./设施数据结构.md#人口归属转化与设施采集区分)）。

## 与设施层关系

| 分层 | 标识 | 说明 |
|------|------|------|
| 配置 | `L5_facility_defs` · `recruitment_office` | 占格类 · 生产类；宿主须为村镇资源点格；`status=defined` |
| 运行时工地 | `FacilitySiteState` | `work_subject_kind=facility_site`；`work_type_id=build_resource_facility` |
| 运行时实例 | `FacilityInstanceState` | `work_subject_kind=facility_instance`；`work_type_id=extract_reserve` |
| 储量 | `VillagePopulationReserveState` | 绑定村镇格；**提取前不计**势力粮食（见 [粮食与周总结-已定案详述](../../01-草稿/归档/粮食与周总结/粮食与周总结-已定案详述.md)） |

## 首版数值（已定）

| 参数 | 值 | 来源 |
|------|-----|------|
| `required_work_amount` | **30** | 满编工程队专精 **3** 回合 |
| `output_per_work_completion` / `default_extract_batch` | **15** 人 | [征兵办](../../02-系统设计/04-资源与人口/荒野地点/征兵办.md) |
| `build_metal_cost` | **30** | [产出锚](../../02-系统设计/04-资源与人口/四种核心资源.md#四类资源产出锚已定) |
| `build_turns` | **3** | `L5_facility_defs` |
| 村镇 `reserve_min` / `reserve_max` | **60** / **120** | [村镇](../../02-系统设计/04-资源与人口/荒野地点/村镇.md)；`L3_resource_defs` |

## 运行时：`VillagePopulationReserveState`

| 字段 | 类型 | 说明 |
|------|------|------|
| `reserve_id` | string | 主键；通常与村镇资源点格 id 1:1 |
| `host_hex_id` | string | 村镇占格 |
| `unaffiliated_headcount` | int | **无归属**可提取储量；首版生成落在 **60～120** |
| `is_active_for_food` | bool | **false** 直至提取；提取后由目标容器接管粮食口径 |

## 运行时：`RecruitmentOfficeInstanceState`（扩展 `FacilityInstanceState`）

| 字段 | 类型 | 说明 |
|------|------|------|
| `facility_instance_id` | string | 与 `FacilityInstanceState` 主键一致 |
| `linked_reserve_id` | string | 指向 `VillagePopulationReserveState` |
| `idle_headcount` | int | **闲置**在设施格、尚未入城或转编制的人口（**无归属**提取后的待命池；可供 [相邻格补员](../../02-系统设计/04-资源与人口/人口与迁移.md#补员--相邻格人员来源已定)） |
| `extract_batch_size` | int | 单次工作结算提取人数；默认 **15**（可被工作效率修正，细则待补） |
| `last_extract_turn_id` | int | 可空；末次成功提取回合 |

## 工作结算：`extract_reserve` → 人口写入

玩家下达 `extract_reserve` 工作后，进度 100% 时按下列顺序结算（**不**在建造完成时自动产出）：

1. 从 `linked_reserve_id.unaffiliated_headcount` 扣减 `extract_batch_size`（默认 **15**）；若储量不足，按**实际剩余**提取（首版）。
2. 写入目标容器（三选一，由玩家指令或接纳流程指定；住房校验失败反馈见 sy-14）：
   - **城区驻留**：`population_type_id=pop_unaffiliated` → 接收城市**城市领袖**管辖池（见 [城市管理系统 · 人力类型名单占位表](../../02-系统设计/04-资源与人口/城市管理系统.md#人力类型名单占位表占位--待策划定案--sy-23)）。
   - **随行人员**：`EscortAccompanyingState`；须来源处预先规划住宅（sy-14 / sy-21 交叉）。
   - **征兵办闲置**：累加至本设施 `idle_headcount`；可供**相邻格** [队伍补员](../../02-系统设计/04-资源与人口/人口与迁移.md#补员--相邻格人员来源已定)（须满足人口归属与类型校验）。
3. **`home_city_ref`**：**不**指向村镇格；关系事件锚定接收方城市领袖所属外部城 / 玩家城（见 [村镇 · 已定](../../02-系统设计/04-资源与人口/荒野地点/村镇.md)）。

## 配置 SO（Unity · 占位）

| 类型 | 用途 |
|------|------|
| `RecruitmentOfficeConfigSO` | 绑定 `facility_type_id=recruitment_office`；`default_extract_batch=15`、`required_work_amount=30`、`build_metal_cost=30` |
| `VillageReserveConfigSO` | 村镇储量初始区间 **60～120**；再生规则仍 **待定** |

## 待实现

- [ ] `VillagePopulationReserveState` 与现有 `CityPopulationPoolState` 拆分对齐（见 [粮食与周总结-已定案详述 · 人口两层](../../01-草稿/归档/粮食与周总结/粮食与周总结-已定案详述.md#23-人口两层活跃容器-vs-村镇储量)）
- [ ] 提取后住房校验与失败反馈（sy-14）
- [ ] 工作效率对 `extract_batch_size` 的修正曲线（首版可先固定 15）

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-10 | 0.0.1 | 初稿占位 |
| 2026-07-11 | 0.0.2 | 对齐产出锚：单次 15、建造 30、储量 60～120 |
