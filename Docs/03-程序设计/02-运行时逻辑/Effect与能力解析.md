> 状态：草稿
> 校验状态：待校验
> 对应规范：[SO配置与能力通道规范](../../00-规范/SO配置与能力通道规范.md)

← [运行时逻辑](./README.md)

# Effect 与能力解析

## 目标

城区能力、队伍能力、设施效果、领袖特质、环境减值统一采用 **GAS-lite** 管线：

- `GameplayEffect`：效果 / Buff / Debuff / 瞬时修正 / 周期效果。
- `GameplayTag`：能力开关、状态与互斥条件。
- `GameplayAbility`：可执行技能薄壳，负责消耗、目标过滤、激活条件与 `executor_key`。
- `AttributeSet`：统一数值命名空间。
- `AbilitySystemComponent`：挂在队伍、城区、格子或势力上的运行时效果容器。

指令表、行动表、响应检测器与 `on_resolve` 作用不并入本管线。

## 程序入口

| 对象 | 程序类型 | 路径 |
|------|----------|------|
| 效果容器 | `AbilitySystemComponent` | `Assets/Scripts/Yanxu.Core/Effects/AbilitySystemComponent.cs` |
| GE 配置 | `GameplayEffectConfigSO` | `Assets/Scripts/Yanxu.Core/Effects/Config/GameplayEffectConfigSO.cs` |
| GA 配置 | `GameplayAbilityConfigSO` | `Assets/Scripts/Yanxu.Core/Effects/Config/GameplayAbilityConfigSO.cs` |
| Tag 注册 | `GameplayTagId` | `Assets/Scripts/Yanxu.Core/Effects/GameplayTagId.cs` |
| Attribute 注册 | `GameplayAttributeId` | `Assets/Scripts/Yanxu.Core/Effects/GameplayAttributeId.cs` |
| 贡献快照 | `EffectContributionSnapshot` | `Assets/Scripts/Yanxu.Core/Effects/EffectContributionSnapshot.cs` |

## Tag 注册表（首版）

| Tag | 说明 |
|-----|------|
| `Capability.Move` | 可执行移动 |
| `Capability.DockToSail` | 可执行离港 |
| `Capability.SailToDock` | 可执行入港 |
| `Capability.ScoutScan` | 可执行侦察扫描 |
| `Capability.ProspectScan` | 可执行勘探扫描 |
| `Capability.Build` | 可执行建造 |
| `Capability.Build.ProductionStorage` | 可建生产/仓储占格类 |
| `Capability.Build.Terrain` | 可建地形类设施 |
| `Capability.Build.Auxiliary` | 可建辅助类设施 |
| `Allow.Build.{facility_type_id}` | **允许设施**；优先级高于地形基础档位 |
| `Capability.TransportCargo` | 可执行搬运 |
| `Capability.District.Academy` | 可激活学院城区能力 |
| `Capability.District.Cannon` | 可激活巨炮城区能力 |
| `District.Academy.Active` | 学院切换式能力已开启 |
| `State.InDarkZone` | 位于暗渊带 |
| `Buff.Wall` | 城墙 Buff 生效 |

> **废止**：`State.Hunger` 及饥饿 cohort 的 GAS 投影**不**纳入本管线；口粮减员由周总结 `FoodAllocationResult` 处理（见 [口粮与周总结（草稿）](../../../01-草稿/口粮与周总结/README.md)）。

## 口粮分配 Override（规划）

领袖能力、人口归属能力可注册 **`IFoodAllocationRuleOverride`**，在周总结口粮分配中**优先执行一轮**（先于 L1→L2→L3 默认比例均分）。示例：**工作者优先**能力（`WorkerPriorityOverride`）——在作用域内先为参与工作的人口配给，剩余 stock 与人口再走默认规则。

| 接口 | 职责 |
|------|------|
| `IFoodAllocationRuleOverride` | 修改 `stock`；对覆盖人口独立完成分到/未分到/减员 |
| `DefaultProportionalDistrictRule` | L1 城区占比 → L2 归属占比 → L3 同比例 |

数据结构与程序占位见 [03-数据字典 · 口粮周总结数据结构](./03-数据字典/README.md#口粮周总结数据结构)。

## Attribute 注册表（首版）

| Attribute | 说明 |
|-----------|------|
| `work_efficiency` | 工作效率，工作开始时快照锁定 |
| `move_speed` | 移动速度倍率 |
| `vision_range` | 视野范围 |
| `defender_loss_reduction` | 防守方人口损失倍率 |
| `headcount_ratio` | 当前人数比 |
| `terrain_path_cost_equiv` | 地形格路径等效格数（hex ASC；见 [地形 capability 目录](../03-数据字典/tables/L1_terrain/terrain_capability_catalog.csv)） |

## 地形格 ASC（hex）

地图格地形层初始化时，按 [terrain_profile_config.csv](../03-数据字典/tables/L1_terrain/terrain_profile_config.csv) 向 **hex `AbilitySystemComponent`** 注册 GA、Apply GE、授予 Tag。能力目录见 [terrain_capability_catalog.csv](../03-数据字典/tables/L1_terrain/terrain_capability_catalog.csv)。

### 地形 Tag（首版）

| Tag | 说明 |
|-----|------|
| `Terrain.Plain` / … / `Terrain.Swamp` | 地形种类 |
| `Capability.Build` | 建造总闸门 |
| `Capability.Build.ProductionStorage` | 生产/仓储占格类 |
| `Capability.Build.Terrain` | 地形类设施 |
| `Capability.Build.Auxiliary` | 辅助类设施 |
| `Capability.Move.Enter` | 允许进入并停留 |
| `Actor.MobileCity` | 移动城市（阻断地形例外） |

### 地形 executor（首版）

| `executor_key` | GA id | 说明 |
|----------------|-------|------|
| `TryTerrainFlatten` | `GA_TerrainFlattenToPlain` | 丘陵平整为平原 |
| `TryBuild` | `TeamCommandKind.BuildFacility` | 建造设施；先查 `Allow.Build.*` |
| `EvaluateMobileCityCrossableFootprint` | `GA_TerrainRule_MobileCityCrossRift` | `mobile_city_passability=crossable` 时校验城区 footprint |

```mermaid
flowchart TD
    Actor["Actor ASC"] --> Tags["TagContainer"]
    Actor --> Attrs["AttributeSet"]
    GE["GameplayEffect"] --> Actor
    GA["GameplayAbility"] -->|"required_tags / blocked_tags"| Tags
    GA -->|"on_activate_effects"| GE
    Attrs --> Work["WorkProgressService"]
    Attrs --> Executor["ExecutorRegistry"]
```

1. 模板或城区初始化时，向 ASC 注册 GA，并 Apply 初始 GE。
2. 指令执行前，按指令类型映射到 `ga_id`，调用 `ASC.TryActivateAbility`。
3. GA 检查 `required_tags` / `blocked_tags`；失败则写 `fail_reason`。
4. GA 激活后可 Apply GE；具体局面变更仍由 executor、工作或交战管线处理。
5. 工作开始时调用 `ASC.GetComputedAttribute("work_efficiency")`，生成 `EffectContributionSnapshot` 并锁定 `work_duration_turn`。

## 废止映射

| 旧对象 | 新对象 |
|--------|--------|
| `ability_set_config` | 模板初始 GE + GA 列表 |
| `ability_channel_config` | `GameplayAbilityConfigSO` |
| `AbilityExecutionGate` | `AbilitySystemComponent.TryActivateAbility` |
| `TeamAbilityCatalogService` | ASC `TagContainer` |
| `IStatModifierProvider` | `GameplayEffectConfigSO.modifiers` |
| `stat_value_channel_entry` | `EffectContributionSnapshot.Entries` |

## 工作时长规则

- `work_efficiency` 的贡献来源只来自 ASC 上的 GE。
- 指挥预览与行动执行必须读取同一 Attribute 合成逻辑。
- 工作开始后锁定 `work_duration_turn`；进行中不因 GE 变化重算。

## 与响应检测器的关系

响应检测器仍是条件检测层：检测通过后触发行为。若行为结果需要施加持续影响（如陷阱造成 debuff），由该行为 Apply GE；检测器本身不注册 GE。

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-06-29 | 0.0.1 | GAS-lite 定案：GE + Tag + GA + AttributeSet 统一管线 |
| 2026-06-30 | 0.0.2 | 废止 State.Hunger；增 IFoodAllocationRuleOverride 规划 |
