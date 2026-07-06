# 配置表 v1.0 · 六边形格地图

> schema_version: **1.0.1**  
> 字段详解：[地图图层配置数据结构.md](../地图图层配置数据结构.md)

## 设计要点（相对旧版）

| 旧版问题 | v1.0 做法 |
|----------|-----------|
| `type_config` + `profile_config` 双表重复 | 每层仅一张 **`L{n}_{layer}_defs.csv`**，一行一类 |
| 枚举散落多文件 | 统一 **`shared/enums.csv`** |
| 建造白名单三张表 | 白名单写在 defs 列；Tag 映射在 **`_program/build_grant_tags.csv`** |
| 设施拆成 profile + terrain_class | 合并进 **`L5_facility_defs.csv`** 宿主格列 |
| 跨层规则重复 defs 内容 | **`L0_cross_modifiers.csv`** 只保留多实体交互 |
| GE 目录给策划看 | 迁入 **`_program/`**，导入管线专用 |
| 每层单独子目录 | **废止**；图层序号写入文件名前缀 |

## 目录

```
tables/
├── L1_terrain_defs.csv
├── L2_environment_defs.csv
├── L3_resource_defs.csv
├── L4_district_defs.csv
├── L5_facility_defs.csv
├── L6_item_defs.csv
├── L0_cross_modifiers.csv
├── shared/              全局枚举、stat 键、合成栈顺序
└── _program/            程序导入映射（策划只读）
```

## 策划工作流

1. 改对应层 **`L{n}_*_defs.csv`**
2. 枚举取值查 **`shared/enums.csv`**
3. 跨层交互（如哨塔+密林）改 **`L0_cross_modifiers.csv`**
4. `status=pending` 表示未定；**不要**在 `_program/` 填玩法数值

## 合成顺序

见 [shared/modifier_stack.csv](./shared/modifier_stack.csv)。
