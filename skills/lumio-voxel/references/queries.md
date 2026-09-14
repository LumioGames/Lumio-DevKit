# 读取与地形物理查询

先确认已满足 [世界与地图](world-and-maps.md) 的 Host 前置条件。本页签名核对于 2026-09-14；以下代码是独立编写的 SDK 用法示例。

## 读格子：先看可用性

`Lumio.GameRuntime.Coordination.IVoxelGameplayQueries` 提供：

```csharp
VoxelCellQuery Read(ulong sectionKey, int cellOffset);
VoxelCellQuery[] Read(IReadOnlyList<(ulong SectionKey, int CellOffset)> cells);
```

结果包含 `HasBlockId`、`Presence`、`ushort BlockId` 和 `ulong SectionRevision`。

| 结果 | 游戏怎样处理 |
| --- | --- |
| `Ready` 且 `HasBlockId` | 可以使用本次方块值和修订；空气判断也必须走到这里 |
| `Unchanged` | 按匹配版本/底图的已有数据解析“未改变”；没有相应基线就不能猜方块值 |
| `Pending` | 等待数据就绪，选格或建造可以显示暂不可用 |
| `Unavailable` | 拒绝依赖该区域的当前操作并展示可提供的原因 |
| 没有 `HasBlockId` | 不使用默认的 `BlockId` 字段作为真实结果 |

下面这个辅助方法采用保守策略，仅接受本次完整读值；是否允许放置还需游戏自己的距离、库存、目标占用等判断。

```csharp
using Lumio.GameRuntime.Coordination;

public static class TerrainRead
{
    public static bool TryReadReady(
        IVoxelGameplayQueries queries, ulong sectionKey, int cellOffset,
        out VoxelCellQuery cell)
    {
        cell = queries.Read(sectionKey, cellOffset);
        return cell.Presence == VoxelPresence.Ready && cell.HasBlockId;
    }
}
```

调用返回 `false` 时只中止这次依赖读值的操作。不要清空世界、把玩家位置改成安全点或关闭整个房间。SDK 抛错是另一条诊断路径，应保存原始异常与操作上下文。

## 查询形状与结果

`IVoxelPhysicsQueries` 使用 `VoxelWorldPoint(float X, float Y, float Z)`：

| 调用 | 输入含义 | 返回中必须检查的字段 |
| --- | --- | --- |
| `Sweep(center, halfExtents, displacement)` | 沿位移扫过轴对齐盒 | `Unresolved`、`Collided`、`TravelFraction` |
| `Raycast(origin, direction, maxDistance)` | 射线方向和距离上限 | `Resolution`、`Collided`、`TravelDistance` |
| `Overlap(center, halfExtents)` | 轴对齐盒重叠 | `Resolution`、`ActualCount`、`Truncated` |

盒的三个半长分量必须有限且严格大于零。射线输入应是有限值、有效方向和合理距离；具体上下限使用当前 SDK 文档。`Overlap` 截断时不能把 `ActualCount` 当全量计数。这里的 Raycast 结果没有命中格坐标或法线字段；选格系统不能凭空读取 `hit.SectionKey` 或 `hit.Normal`，应使用已交付的更完整查询面或项目现有的目标格解析。

本例只计算一个盒体允许前进的比例，调用方在自身移动逻辑中使用结果：

```csharp
using System;
using Lumio.GameRuntime.Coordination;

public static class TerrainMotion
{
    public static bool TryMeasureTravel(
        IVoxelPhysicsQueries physics,
        VoxelWorldPoint center, VoxelWorldPoint halfExtents,
        VoxelWorldPoint displacement, out double fraction)
    {
        fraction = 0;
        VoxelSweepHit hit = physics.Sweep(center, halfExtents, displacement);
        if (hit.Unresolved) return false;
        if (!double.IsFinite(hit.TravelFraction) ||
            hit.TravelFraction < 0 || hit.TravelFraction > 1)
            throw new InvalidOperationException("体素扫掠返回无效比例。");
        if (!hit.Collided && hit.TravelFraction != 1)
            throw new InvalidOperationException("已解析的未命中结果必须允许完整行程。");
        fraction = hit.TravelFraction;
        return true;
    }
}
```

`Unresolved` 是地形在本次查询切面中不足以回答，不能作为 `Miss`、`Hit` 或空气使用。查询本身不等于请求加载；不能靠循环重查强迫地形出现，也不能用另一次格读取否定物理查询的 `Unresolved`。交给 Host 的驻留/流式加载策略后，在后续时机再尝试。

## 接到 GAS 移动前先核对形状

`Lumio.GameRuntime.Gas.IAbilityPhysicsPort.Sweep(Vector3 origin, Vector3 displacement, float radius)` 声明的是球体扫掠。它与上述 AABB 扫掠既有形状差异，也有结果差异：`AbilitySweepHit` 没有 `Unresolved` 字段。

用 `halfExtents=(radius,radius,radius)` 调 AABB 查询不能获得等价球体碰撞。返回 `AbilitySweepHit(false, 1, ...)` 也不能表达未知地形。若 SDK 尚未交付保留形状和未知态的适配器，应明确报告接缝缺失，保持这次移动被拒绝并暴露诊断，不自行写碰撞内核或静默安装测试替身。

Sample 当前 `SampleGameplay` 会装配 `RecordingAbilityPhysicsPort`，它返回无碰撞；`MoveAbility.Execute` 还存在 `catch (Exception)`。这两处可用于了解调用位置，但不构成真实地形阻挡证明，也不是新游戏应复制的异常处理模板。

## 如何确认接通

至少观察：已加载空地完整通过、已加载墙体限制行程、未就绪区域拒绝当前查询、无效形状保留具体错误。同一场景分别确认 Server 与 Client Replica 使用正确世界。替身测试只证明游戏分支，真实地形效果需相应 Native/Host 运行证据，记录 SDK 身份、地图版本、操作和查询结果。

公开阅读入口：[Sample 物理端口装配](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/src/Lumio.Sample.Gameplay/SampleGameplay.cs)、[移动技能调用位置](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/src/Lumio.Sample.Gameplay/Abilities/MoveAbility.cs)。
