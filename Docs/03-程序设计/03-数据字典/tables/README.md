# 配置表 v1.0 · 六边形格地图

> schema_version: **1.0.0**  
> 字段详解：[地图图层配置数据结构.md](../地图图层配置数据结构.md)

## 设计要点（相对旧版）

| 旧版问题 | v1.0 做法 |
|----------|-----------|
| `type_config` + `profile_config` 双表重复 | 每层仅 **`{layer}_defs.csv`**，一行一类 |
| 枚举散落多文件 | 统一 **`shared/enums.csv`** |
| 建造白名单三张表 | 白名单写在 defs 列；Tag 映射在 **`_program/build_grant_tags.csv`** |
| 设施拆成 profile + terrain_class | 合并进 **`facility_defs.csv`** 宿主格列 |
| 跨层规则重复 defs 内容 | **`L0_cross/cross_modifiers.csv`** 只保留多实体交互 |
| GE 目录给策划看 | 迁入 **`_program/`**，导入管线专用 |

## 目录

```
tables/
├── shared/           全局枚举、stat 键、合成栈顺序
├── L1_terrain/       terrain_defs.csv
├── L2_environment/   environment_defs.csv
├── L3_resource/      resource_defs.csv
├── L4_district/      district_defs.csv
├── L5_facility/      facility_defs.csv
├── L6_item/          item_defs.csv
├── L0_cross/         cross_modifiers.csv
└── _program/         程序导入映射（策划只读）
```

## 策划工作流

1. 改对应层 **`{layer}_defs.csv`**
2. 枚举取值查 **`shared/enums.csv`**
3. 跨层交互（如哨塔+密林）改 **`L0_cross/cross_modifiers.csv`**
4. `status=pending` 表示未定；**不要**在 `_program/` 填玩法数值

## 合成顺序

见 [shared/modifier_stack.csv](./shared/modifier_stack.csv)。
