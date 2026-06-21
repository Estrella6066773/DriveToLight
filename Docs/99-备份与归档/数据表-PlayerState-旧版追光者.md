> 状态：草稿
> schema_version: 0.1.0
> 数据层级：L1 实现

# 数据表：PlayerState

## 字段定义

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| CurrentLight | int | >= 0 | 0 | 当前持有光源量 |
| MaxLight | int | > 0 | 100 | 光源上限 |
| CurrentRegion | string | FK→Region | "" | 当前所在区域 |
| UnlockedAbilities | List<string> | | [] | 已解锁能力 ID |

## 约束

- CurrentLight 不超过 MaxLight。
- 能力 ID 必须在 AbilityDef 中存在。

## 示例

```json
{
  "CurrentLight": 30,
  "MaxLight": 100,
  "CurrentRegion": "Region_District_01",
  "UnlockedAbilities": ["Ability_Dash", "Ability_LightPulse"]
}
```

## 修订记录

| 日期 | schema_version | 说明 |
|------|----------------|------|
| 2026-06-20 | 0.1.0 | 初稿 |
