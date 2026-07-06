# 配置表（CSV）

本目录存放**可调数值与枚举参数**的权威 CSV。字段语义与约束以同名的 Markdown 数据字典为准；程序与关卡工具应**优先读取 CSV**，设计文档中的表格仅作说明或链入此处。

## 约定

| 项 | 说明 |
|----|------|
| **编码** | UTF-8（无 BOM） |
| **换行** | LF |
| **主键** | 首列 `*_id`，全表唯一 |
| **空单元格** | 表示「未定」或「不适用」 |
| **列表字段** | 同一单元格内用 **分号 `;`** 分隔（避免与 CSV 逗号冲突） |
| **玩法差异** | 优先拆为 [terrain_capability_catalog.csv](./terrain_capability_catalog.csv) 中的 GE/GA，经 [terrain_profile_config.csv](./terrain_profile_config.csv) 装配，**禁止**在 `terrain_type_config` 写布尔规则列 |
| **修订** | 改 CSV 时同步更新对应 Markdown 数据字典修订记录 |

## 当前表

| 文件 | 说明 |
|------|------|
| [terrain_type_config.csv](./terrain_type_config.csv) | 地形枚举 → profile 引用 |
| [terrain_profile_config.csv](./terrain_profile_config.csv) | 每地形 SO 装配：GE / GA / Tag |
| [terrain_capability_catalog.csv](./terrain_capability_catalog.csv) | 地形专属能力目录（须实现的 SO + executor） |

完整说明见 [地形类型配置数据结构.md](../地形类型配置数据结构.md)。
