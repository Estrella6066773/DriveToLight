# _program · 导入管线（策划只读）

由程序根据 `*_defs.csv` 生成或校验；**不在此填玩法平衡数值**。

策划主表使用中文列名时，导入经 [column_registry.csv](../shared/column_registry.csv) 与 [enums.csv](../shared/enums.csv) 反查程序键。

| 文件 | 说明 |
|------|------|
| [ge_catalog.csv](./ge_catalog.csv) | defs 列 → GE/GA |
| [build_grant_tags.csv](./build_grant_tags.csv) | `facility_id` → `Allow.Build.*` |

能力自然语言见 [能力说明.csv](../shared/能力说明.csv)。
