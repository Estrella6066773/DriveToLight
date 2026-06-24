> 状态：草稿
> 校验状态：不适用

# 引擎映射

本目录存放 C# 模块、ScriptableObject 资产路径与 Unity 场景/Prefab 的对应关系。

> 当前项目 **尚无运行时代码**；下表为规划占位，待 `Assets/Scripts/` 创建后逐条落实。

## 规划目录结构

| 模块 | 脚本路径（规划） | SO 配置路径（规划） | 关联程序设计 |
|------|------------------|---------------------|--------------|
| Core | `Assets/Scripts/Core/` | — | [模块划分](../01-架构总览/模块划分.md) |
| Turn | `Assets/Scripts/Turn/` | `Assets/Resources/Config/Turn/` | [回合与行动数据结构](../03-数据字典/回合与行动数据结构.md) |
| Team | `Assets/Scripts/Team/` | `Assets/Resources/Config/Team/` | [队伍与战斗数据结构](../03-数据字典/队伍与战斗数据结构.md) |
| Communication | `Assets/Scripts/Communication/` | `Assets/Resources/Config/Comm/` | [通讯与视野同步数据结构](../03-数据字典/通讯与视野同步数据结构.md) |
| Map | `Assets/Scripts/Map/` | `Assets/Resources/Config/Map/` | 待建地图表 |
| City | `Assets/Scripts/City/` | `Assets/Resources/Config/City/` | 待建城区表 |

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-06-22 | 0.0.1 | 初稿：规划目录占位，待代码落地后补 Prefab/场景映射 |
