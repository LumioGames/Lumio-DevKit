# 建造、破坏与挖穿

本页消费面核对于 2026-09-14。读取前置见 [查询](queries.md)，体素与实体的分工见 [世界与地图](world-and-maps.md)。

## 玩法先判断，端口再接收意图

放置需要目标格、拟放方块、玩家权限/距离/库存等游戏判断。挖掘需要有效目标、工具、体力和储量。客户端可请求操作和做 Local 表现，权威结果由 Server 决定。

`IVoxelGameplayWrites` 提供：

```csharp
VoxelDigResult Write(IReadOnlyList<VoxelWriteEntry> entries, string txnId);
VoxelDigResult DigThrough(ulong section, int cell, ulong expectedRevision, string txnId);
```

`VoxelWriteEntry` 参数依次是 `ulong SectionKey`、`int CellOffset`、`ushort BlockId`、`ulong ExpectedSectionRevision`。修订取自目标格读取的 `SectionRevision`，不填 `WorldRevision`，不写常量零来绕过并发检查。

这个独立示例只排入一格建材写入；它不承担权限、扣物品或提交调度：

```csharp
using Lumio.GameRuntime.Coordination;

public static class BuildingIntent
{
    public static bool TryQueuePlacement(
        IVoxelGameplayQueries queries, IVoxelGameplayWrites writes,
        ulong sectionKey, int cellOffset, ushort blockId, string txnId,
        out VoxelDigResult queued)
    {
        queued = default;
        VoxelCellQuery cell = queries.Read(sectionKey, cellOffset);
        if (cell.Presence != VoxelPresence.Ready || !cell.HasBlockId)
            return false;
        queued = writes.Write(new[]
        {
            new VoxelWriteEntry(sectionKey, cellOffset, blockId, cell.SectionRevision)
        }, txnId);
        return true;
    }
}
```

`true` 表示端口接收了意图，不证明变更已经落地。返回的 `VoxelDigResult` 只有 `CommitId`，没有 `Succeeded` 或“已掉落”字段。让现有 Host/Runtime 的 Tick 接线完成应用，不能在技能里补调一个手写提交循环。

同一逻辑操作的重试保留同一事务身份；改变目标或内容是另一操作，必须按游戏命令的身份规则处理。若出现修订冲突，先重读再重新评估玩法条件，不换一个修订盲目重放扣费，也不直接覆盖别人的建造结果。

## 挖穿有业务实体的格子

普通地形破坏和带实体绑定的矿脉不是同一个动作。`DigThrough` 排入格子变空气和绑定清理；当前 Host 适配层可以在绑定到实际 ECS World 后为关联实体排入销毁命令。没有真实 World 或提交接线，不能认为 ECS 那半已经完成。

`DigThrough` 不创建矿石，不决定体力费用或掉落概率。完整矿脉玩法应把这些部分放到一致的业务提交路径中：

1. 读格子与实体，核对储量、距离、权限、体力和预期修订。
2. 未挖穿时只做游戏规定的储量/体力变更；挖穿时把空气写入、绑定清理和实体结果交给协调提交。
3. 根据已确认的应用结果产生掉落与复制；同一确认重放不得再掉一份矿。

当前 `HostVoxelWorldAdapter` 暴露 `TransactionState(txnId)`、`AppliedDigs` 和 `DigApplied`，可供已接入的宿主/游戏系统观察原生应用。不要把“通知已触发”直接当持久化证明，也不要据此宣称某个新扣费/掉落实现具有跨域原子性。业务产生实体应沿现有 ECS 命令和 Tick 顺序，不从 Native 回调里直接改世界。

## Sample 接缝的实际含义

公开样例的 `ISampleVoxelBinding.TryBind(...)` 与 `ISampleVoxelWriter.TryWriteAir(NetEntityId)` 是 **Sample 自己的宿主注入口**，不是 SDK 通用体素 API。`MineAbility.Writer == null` 或 `TryWriteAir` 返回 `false` 时，挖穿请求没有完成；示例在该分支避免后续扣费和掉矿。

即使 Writer 返回 `true`，也要核查具体适配器把它定义为“已排队”还是“已提交”。它的 bool 本身无法证明格子、库存、储量、掉落和存档属于同一耐久事务。不能把这个小接口直接包装成“原子建造系统”。

普通失败（够不着、没体力、目标不再有效、格子未准备好）只影响当前操作。Native 错误、错误版本、损坏快照或不兼容 SDK 应输出具体错误；不要捕获所有异常后返回成功、装 Recording 端口或替换成空世界。

## 验证一个可用切片

- 放置后通过权威读确认方块与新修订，再观察客户端更新。
- 两个请求操作同一格时，确认冲突不会重复扣费或静默覆盖。
- 同一操作重试后确认格子、绑定、实体、掉落各发生一次预期变化。
- 缺块或 Writer 未接入时确认没有扣费、掉落或假成功提示。
- 若声称可保存：真实关服重启后核对格子、实体与库存；单元测试、应用回执和底图可读取都不能替代这一步。

公开样例：[宿主注入口](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/src/Lumio.Sample.Gameplay/ISampleVoxelBinding.cs)、[挖掘入口](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/src/Lumio.Sample.Gameplay/Abilities/MineAbility.cs)、[服务端执行分支](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/src/Lumio.Sample.Gameplay/Abilities/MineAbility.Server.cs)。
