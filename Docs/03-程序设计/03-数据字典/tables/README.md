# 配置表（CSV）· 六边形格地图

按**地图图层**分子目录存放；目录名带 **`Ln_` 前缀**（n = 栈序）。字段详解见 [地图图层配置数据结构.md](../地图图层配置数据结构.md)。

## 目录结构

```
tables/
├── L1_terrain/        地形层
├── L2_environment/    环境层
├── L3_resource/       资源层
├── L4_district/       建筑层（城区）
├── L5_facility/       设施层
├── L6_item/           物品层
└── L0_interaction/    跨图层影响规则（非栈层，n=0）
```

## 约定

| 项 | 说明 |
|----|------|
| **编码** | UTF-8（无 BOM）· **换行** LF |
| **主键** | 首列 `*_id` 全表唯一 |
| **策划主表** | 各层 `*_profile_config.csv` |
| **待定** | 填 `pending` 或留空 |

## 各层入口

| 目录 | 策划主表 | 字段说明 |
|------|----------|----------|
| [L1_terrain/](./L1_terrain/) | `terrain_profile_config.csv` | [地形类型配置数据结构.md](../地形类型配置数据结构.md) |
| [L2_environment/](./L2_environment/) | `environment_profile_config.csv` | [地图图层配置数据结构.md §L2](../地图图层配置数据结构.md#l2-环境层) |
| [L3_resource/](./L3_resource/) | `resource_point_profile_config.csv` | [地图图层配置数据结构.md §L3](../地图图层配置数据结构.md#l3-资源层) |
| [L4_district/](./L4_district/) | `district_profile_config.csv` | [地图图层配置数据结构.md §L4](../地图图层配置数据结构.md#l4-建筑层城区) |
| [L5_facility/](./L5_facility/) | `facility_type_profile_config.csv` | [设施数据结构.md](../设施数据结构.md) |
| [L6_item/](./L6_item/) | `item_profile_config.csv` | [地图图层配置数据结构.md §L6](../地图图层配置数据结构.md#l6-物品层) |
| [L0_interaction/](./L0_interaction/) | `layer_interaction_rule_config.csv` | [地图图层配置数据结构.md §图层间](../地图图层配置数据结构.md#图层间影响规则) |

## 运行时合成顺序

1. `L1_terrain/` profile 基线  
2. `L2_environment/` 修正  
3. `L5_facility/` 有效地形类设施覆盖  
4. 建造白名单（`L1_terrain/`、`L3_resource/`）  
5. `L0_interaction/` 按 `priority` 叠算  
