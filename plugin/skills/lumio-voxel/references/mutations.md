# 建造、破坏与挖穿

本页消费面按 Engine v0.0.2 核对。读取前置见 [查询](queries.md)，体素与实体的分工见 [世界与地图](world-and-maps.md)。

## 玩法先判断，端口再接收意图

放置需要目标格、拟放方块、玩家权限/距离/库存等游戏判断。挖掘需要有效目标、工具、体力和储量。客户端可请求操作和做 Local 表现，权威结果由 Server 决定。

Sample 没有提供通用的“放置建材”技能或 `TryStageMutation` 包装器；不要从接口名称猜一套新的 `BuildingIntent` API。当前公开接线只展示挖穿：`MineAbility.Client.cs` 和 `SampleMiningComponent.Server.cs` 都先从 `HostVoxelWorldAdapter` 读出格子，再以读取到的 `SectionRevision` 排入操作。

客户端预测分支的实际代码摘录（文件：[`Gameplay/Abilities/MineAbility.Client.cs`](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Abilities/MineAbility.Client.cs)）：

```csharp
VoxelCellQuery read = resolved.Read(section, offset);
PredictedDigVerdict verdict = ClassifyPredictedDig(true, read.HasBlockId, read.BlockId,
    read.HasBlockId ? resolved.BindingGet(section, offset) : null, reserve.Entity.ToHex());
```

同一文件随后在订单分支中使用读取到的修订：

```csharp
VoxelStageResult result = adapter!.TryStageDigThrough(sectionKey, cellOffset, cell.SectionRevision, transaction);
ordered = result.Status == VoxelStageStatus.Staged;
```

服务端由 [`Gameplay/Abilities/MineAbility.Server.cs`](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Abilities/MineAbility.Server.cs) 转交 `SampleMiningComponent.StageFinal`；真正的权威排入在 [`Gameplay/SampleMiningComponent.Server.cs`](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/SampleMiningComponent.Server.cs)：

```csharp
VoxelStageResult result = adapter.TryStageCoalescibleDigThrough(sectionKey, cellOffset,
    cell.SectionRevision, transaction);
```

`Staged` 表示端口接受了意图，不证明变更已经落地。让 Runtime 在 Tick 提交阶段应用，不能在技能里补调手写提交循环。同一逻辑操作的重试保留同一事务身份；改变目标或内容是另一操作，必须按游戏命令的身份规则处理。若出现修订冲突，先重读再重新评估玩法条件，不换一个修订盲目重放扣费，也不直接覆盖别人的建造结果。

## 挖穿有业务实体的格子

普通地形破坏和带实体绑定的矿脉不是同一个动作。Sample 的 `TryStageDigThrough`/`TryStageCoalescibleDigThrough` 排入格子变空气和绑定清理；在真实 World 中，关联实体的销毁沿 ECS 结构命令和 Tick 顺序处理。没有真实 World 或提交接线，不能认为 ECS 那半已经完成。

挖穿不创建矿石，不决定体力费用或掉落概率。完整矿脉玩法应把这些部分放到一致的业务提交路径中：

1. 读格子与实体，核对储量、距离、权限、体力和预期修订。
2. 未挖穿时只做游戏规定的储量/体力变更；挖穿时把空气写入、绑定清理和实体结果交给协调提交。
3. 根据已确认的应用结果产生掉落与复制；同一确认重放不得再掉一份矿。

`HostVoxelWorldAdapter` 的事务状态与结果回读只说明 Runtime 已报告该事务的阶段；通知本身不能证明持久化。业务产生实体应沿现有 ECS 命令和 Tick 顺序，不从 Native 回调里直接改世界。

## Sample 接缝的实际含义

公开样例的 `MineAbility.Client.cs` 调用 `HostVoxelWorldAdapter.TryStageDigThrough`，而 `MineAbility.Server.cs` 通过 `SampleMiningComponent.StageFinal` 调用 `TryStageCoalescibleDigThrough`。客户端走 GAS 预测会话，服务端把待结算记录写入 `PendingDigComponent`；预测记录、撤销与重放由 GAS 管理，玩法不手写 Undo。客户端无法定位自己的 Section/cell 时，`SampleMiningComponent.TryLocate` 返回 `false`，调用方把它当作尚未知道，而不是把未知当空气。

普通失败（够不着、没体力、目标不再有效、格子未准备好）只影响当前操作。Native 错误、错误版本、损坏快照或不兼容 SDK 应输出具体错误，不用空世界掩盖。

## 验证一个可用切片

- 放置后通过权威读确认方块与新修订，再观察客户端更新。
- 两个请求操作同一格时，确认冲突不会重复扣费或静默覆盖。
- 同一操作重试后确认格子、绑定、实体、掉落各发生一次预期变化。
- 缺块或宿主适配器未接入时确认没有扣费、掉落或假成功提示。
- 若声称可保存：真实关服重启后核对格子、实体与库存；单元测试、应用回执和底图可读取都不能替代这一步。

公开样例：[挖掘入口](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Abilities/MineAbility.cs)、[服务端执行分支](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Abilities/MineAbility.Server.cs)、[客户端预测分支](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Abilities/MineAbility.Client.cs)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
