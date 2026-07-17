# SO 配置与能力通道规范

## 目标

统一项目实现口径：**参数全部走 ScriptableObject（SO）配置，程序只负责 GameplayEffect / GameplayAbility 执行流程**。

本规范适用于 `Docs/02-系统设计/` 与 `Docs/03-程序设计/` 的所有新增与修订文档。

## 核心原则

1. **参数配置化**
 - 队伍、单位、能力、战斗、建造、搬运、勘探等业务参数，必须通过 SO 配置。
 - 禁止在程序中写死平衡参数、默认值与阈值（仅允许编辑器兜底值与空值保护）。

2. **GAS-lite 管线**
 - 一切 Buff、Debuff、瞬时修正、周期效果使用 `GameplayEffectConfigSO`。
 - 一切可执行技能使用 `GameplayAbilityConfigSO`，程序只提供 `executor_key` 对应入口（例如 `TryBuild`、`TryTransport`、`TryAttack`）。
 - 能力是否可用由 `GameplayTag` 控制；数值由 `AttributeSet` 与 GE 贡献明细合成。

3. **模板组合化**
 - 队伍种类视为模板预设，本质为“初始 GE / GA 列表 + 参数配置”。
 - 模板可复用同一 GA，不同模板通过不同 GE 与参数表现差异。
 - **地形类型**：`L1_terrain_defs` 描述**格基线**；通道/桥梁等**地形类设施**的有效时覆盖在 `FacilityTypeConfigSO` / [L5_facility_defs.csv](../03-程序设计/03-数据字典/tables/L5_facility_defs.csv)，**不**列入地形 capability 目录。

4. **引擎内配置**
 - 默认由开发者在 Unity 编辑器内完成 SO 资产配置与装配。
 - 可使用 MCP 代为批量创建、挂载、校验 SO 资产，但不改变“配置权在 SO”的原则。

5. **数值通道**
 - 合成类数值（如 **工作效率** → 工作时长）须通过 GE 贡献快照记录每一项修正的**来源**、**运算方式**与**数值**。
 - 运行时写入 `EffectContributionSnapshot`（并保留 `work_efficiency_snapshot` 等工作快照），**指挥预览与行动执行共用同一结算管线**。
 - 玩家界面须能罗列并展示通道明细；禁止仅在 UI 层硬编码说明文字而不落运行时记录。

6. **策划可读配置表**
 - 系统策划维护的 CSV 主表使用**中文列名**与**自然语言能力说明**；见 [策划可读配置表规范](./策划可读配置表规范.md)。
 - 程序键、Tag 与 GE/GA 映射下沉 `_program/`；导入经 `column_registry` 与 `enums` 反查。

## 禁止事项

- 在运行时代码中用 `if (队伍类型 == X) then 固定能力` 写死玩法能力。
- 在代码常量中固化可调平衡参数（攻击效果、负载上限、建造速度、视野等）。
- 在文档中只写“程序计算”而不提供对应 SO 字段来源。
- 在模块内另建独立 Buff 表或 `*CapabilityService`，绕过 GE / GA 管线。

## 必备设计要素

每个可执行技能在文档中至少要有以下字段：

- `ability_id`（技能 ID）
- `required_tags` / `blocked_tags`（启用与互斥条件）
- `executor_key`（程序入口键）
- `on_activate_effects`（激活时施加的 GE）
- `target_filter`（目标过滤）
- `rule_guard`（前置条件）
- `cooldown` 与 `action_point_cost`（若该能力需要）

## 文档落地要求

1. 在系统设计文档中，说明 GE / GA / Tag 与模板组合关系，不写死“类型=能力”。
2. 在程序设计文档中，给出 SO 表结构、字段约束、运行时读取流程。
3. 在数据字典中，给出至少一份可执行示例（模板、GE、GA、Tag、Attribute）。

## 版本与修订

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-06-22 | 0.0.1 | 初稿：确立“参数全部走 SO，程序只做通道与执行”为项目级实现规范 |
| 2026-06-22 | 0.0.2 | 补充数值通道：修正来源记录、展示与预览/执行一致要求 |
| 2026-06-29 | 0.0.3 | 能力通道升级为 GAS-lite：GameplayEffect + GameplayAbility + GameplayTag + AttributeSet |
| 2026-07-06 | 0.0.4 | 地形 profile 组合化；地形类设施覆盖归属设施 SO |
| 2026-07-06 | 0.0.5 | 地形格基线与地形类设施基本能力分表 |
| 2026-07-07 | 0.0.6 | 链至策划可读配置表规范 |
