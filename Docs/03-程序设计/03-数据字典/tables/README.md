# 配置表（CSV）· 六边形格地图图层

本目录存放**地图各图层**的可调数值权威 CSV。总览与字段说明见 [地图图层配置数据结构.md](../地图图层配置数据结构.md)。

## 统一约定

| 项 | 说明 |
|----|------|
| **编码** | UTF-8（无 BOM）· **换行** LF |
| **主键** | 首列 `*_id` 全表唯一 |
| **空单元格** | 不适用或继承默认 |
| **列表** | 分号 `;` 分隔 |
| **待定** | 单元格填 `pending` 或留空；`config_status=pending` |
| **策划主表** | `*_profile_config.csv` — **改这里** |

## 表型（每层）

```
{layer}_type_config.csv     枚举速查
{layer}_profile_config.csv  权威玩法参数（一行一类）
{layer}_*_enum.csv          专用枚举（可选）
```

## 按图层索引

### L1 地形层（已定框架）

| 文件 | 说明 |
|------|------|
| [terrain_type_config.csv](./terrain_type_config.csv) | 地形枚举速查 |
| [terrain_profile_config.csv](./terrain_profile_config.csv) | **地形格基线** |
| [mobile_city_passability_enum.csv](./mobile_city_passability_enum.csv) | 移动城市通行性 |
| [facility_build_allow_catalog.csv](./facility_build_allow_catalog.csv) | 建造白名单 → GE |
| [facility_terrain_class_config.csv](./facility_terrain_class_config.csv) | 地形类设施有效时覆盖 |
| [terrain_capability_catalog.csv](./terrain_capability_catalog.csv) | 程序 GE/GA 映射 |

详见 [地形类型配置数据结构.md](../地形类型配置数据结构.md)。

### L2 环境层

| 文件 | 说明 |
|------|------|
| [environment_type_config.csv](./environment_type_config.csv) | 环境类型速查 |
| [environment_profile_config.csv](./environment_profile_config.csv) | **环境效果主表** |
| [environment_subtype_enum.csv](./environment_subtype_enum.csv) | 地面表层 / 天气 / 轨迹 |
| [environment_stack_rule_enum.csv](./environment_stack_rule_enum.csv) | 堆叠规则 |

### L3 资源层

| 文件 | 说明 |
|------|------|
| [resource_point_type_config.csv](./resource_point_type_config.csv) | 资源点速查 |
| [resource_point_profile_config.csv](./resource_point_profile_config.csv) | **储量、揭示、白名单** |
| [resource_point_facility_allow.csv](./resource_point_facility_allow.csv) | 白名单 → GE（与 profile 同步） |

### L4 建筑层（城区）

| 文件 | 说明 |
|------|------|
| [district_type_config.csv](./district_type_config.csv) | 城区类型速查 |
| [district_profile_config.csv](./district_profile_config.csv) | **承载、负载成本、设施位** |
| [district_category_enum.csv](./district_category_enum.csv) | 特殊 / 一般 |
| [district_state_enum.csv](./district_state_enum.csv) | 正常 / 废墟 |

### L5 设施层

| 文件 | 说明 |
|------|------|
| [facility_type_config.csv](./facility_type_config.csv) | 设施类型速查 |
| [facility_type_profile_config.csv](./facility_type_profile_config.csv) | **建造、耐久、分类参数** |
| [facility_terrain_class_config.csv](./facility_terrain_class_config.csv) | 地形类设施宿主格覆盖 |

### L6 物品层

| 文件 | 说明 |
|------|------|
| [item_type_config.csv](./item_type_config.csv) | 物品类型速查 |
| [item_profile_config.csv](./item_profile_config.csv) | **堆叠、搬运** |

### 跨图层

| 文件 | 说明 |
|------|------|
| [layer_interaction_rule_config.csv](./layer_interaction_rule_config.csv) | 图层间影响规则（含 priority） |

## 合成结算顺序（运行时）

1. 地形 profile 基线  
2. 环境 profile 修正（`path_cost_delta` 等）  
3. 有效地形类设施覆盖  
4. 资源点 / 建造白名单（`TryBuild`）  
5. [layer_interaction_rule_config](./layer_interaction_rule_config.csv) 按 `priority` 叠算  
