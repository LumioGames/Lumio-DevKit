# Tick 顺序

Tick（逻辑帧）把玩家输入、玩法系统、地形与实体修改、同步发送按固定顺序推进，让同一操作有明确的生效时间。

## 玩家挖一下矿时发生什么

1. 服务器处理本帧输入时，GAS（玩法技能系统）检查 `MineAbility` 的目标、距离、体力与冷却。普通一击直接扣体力和储量；最后一击先排入地形操作与 `PendingDigComponent` 等待记录。
2. 本帧业务系统运行。`Gameplay/SampleMiningSystem.Server.cs` 的 `SampleMiningSystem` 在 `ProcessorPlan` 调用 `SampleMiningComponent.Advance()`；它先结算已返回的地形结果，再推进矿脉扫描与绑定。刚排入的最后一击此时还没有经过本帧的地形提交。
3. 后面的 `VoxelCommit` 阶段应用挖掘：方块变空气、格子绑定改变。`DigApplied` 回调只核对和记录变化，不在回调里扣体力或发矿。
4. 后续一帧的 `ProcessorPlan` 再从 `DrainResults().Results` 取到结果。`Settle` 按 `PendingDigComponent.Serial` 排序，成功才调用 `Pay` 扣体力并排入 `OreDropEntity`；拒绝则清理记录，不发奖励。
5. 掉落在该帧的实体提交阶段创建，随后同步给客户端。玩家捡矿时先清空矿堆并排入效果与销毁；同一帧提交实体命令后结算 `PickupOreEffect`，再把结果发出去。

完整技能流程见 [GAS 技能](gas-abilities.md)。`Gameplay/EntityTypes/WorldEntity.cs` 声明 `TickRateHz = 20`，即每秒 20 个逻辑帧；不要用渲染帧率或另一个计时器推进冷却。

## 一帧的完整顺序

以下编号从 1 开始；`TickPhase` 枚举值从 0 开始，因此表中第 9 步对应枚举值 8。引擎依次经过这 13 个阶段，玩法系统只能登记到第 3、4 步。

| 顺序 | 阶段 | 在这一段做什么 |
| --- | --- | --- |
| 1 | `IngressCapture` | 按本帧消息与字节预算，从宿主输入队列取出一批消息。 |
| 2 | `DecodeAndCanonicalize` | 输入解码和统一格式的阶段位置。 |
| 3 | `ApplyInputs` | 服务器处理到期事件与本批输入，执行技能或 RPC；然后执行登记在此阶段的系统。客户端在此应用收到的控制与同步消息。 |
| 4 | `ProcessorPlan` | 执行玩法业务系统，例如 `SampleMiningSystem`；读取已有状态、写允许修改的字段，并排入地形或实体命令。 |
| 5 | `CrossWorldPrepare` | 调用已绑定的跨世界准备处理，把关联修改准备好。 |
| 6 | `NativeJobBarrier` | 收集原生作业完成结果的阶段位置。 |
| 7 | `CommitDecision` | 调用已绑定的提交决策处理。 |
| 8 | `VoxelCommit` | 提交地形与格子绑定修改，产生可供后续业务阶段读取的结果。 |
| 9 | `EcsCommandBufferCommit` | 提交 ECS（实体组件系统）中的创建、销毁命令；服务器随后结算排队的即时效果。 |
| 10 | `GasAndEventFinalize` | 完成本帧 GAS 记录、空间索引、保存请求与效果通知等收尾；之后才进入面向客户端的结果整理。 |
| 11 | `ReplicationProjection` | 根据观察范围和字段权限，整理发给各客户端的同步内容。 |
| 12 | `SnapshotHashMetrics` | 快照摘要与运行指标的阶段位置。 |
| 13 | `EgressPublish` | 完成帧末处理、推进逻辑帧号、清理本帧临时数据，由宿主取走待发消息。 |

第 2、6、12 步在 v0.0.2 默认世界入口中尚未接入额外处理，当前回调为空；阶段存在不表示每帧都执行了解码、原生作业或快照统计。第 5、7、8 步调用宿主绑定的处理。写玩法时使用已接好的宿主与业务阶段，不自行补一套引擎循环。

## 怎样写系统

Sample 系统原文摘自 [`Gameplay/SampleMiningSystem.Server.cs`](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/SampleMiningSystem.Server.cs)，提交 `f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb`，许可证 Apache-2.0：

```csharp
[System(TickPhase.ProcessorPlan)]
public sealed class SampleMiningSystem : EcsSystem
{
    public override void Execute(World world) => world.Single<SampleMiningComponent>().Advance();
}
```

修改声明后 [重新生成注册表](code-generation.md)。服务器的 `Gameplay/generated/server/Lumio.Sample.Gameplay.Registry.g.cs` 包含该系统；客户端不登记它。

- 只在 `ApplyInputs` 或 `ProcessorPlan` 登记玩法系统。系统顺序在世界启动时确定；新增注册要重新创建世界。
- 同阶段依赖按先后关系排序，没有依赖关系的系统按稳定 ID 排序，不依赖文件顺序。缺失依赖、依赖循环、重复 ID，以及同阶段多个系统声明写同一组件都会被拒绝。多系统依赖与读写声明的完整例子在示例中尚未提供。
- 在业务阶段读取组件、计算规则；实体创建与销毁排入 `World.Commands`，到第 9 步才应用。跨帧等待信息放在组件里，例如有 `[Persist]` 的 `PendingDigComponent`，不要存在每次新建的系统实例字段中。
- 体素回调只观察结果，不能在 `DigApplied` 中写同步字段或创建、销毁实体。挖掘扣费和掉落等待后续业务阶段读到实际结果。
- 客户端预测使用 GAS；普通客户端系统不能直接发放服务器库存、奖励或掉落。地形请求已排入、未知分块或修订冲突都不等于成功。

如果系统没有运行，先核对编译端、生成注册表和登记阶段；若成功回调已经出现却没有掉落，继续检查后续帧的 `Settle` 结果与实体命令提交。体素细节见 [体素写入](../../lumio-voxel/references/mutations.md)，宿主启动见 [服务器技能](../../lumio-server/SKILL.md)。

核对阶段 API 时，从 [公开 SDK 参考入口](../../lumio-development/references/getting-started.md) 查安装包里的 `Lumio.GameRuntime.Primitives.xml`、`Lumio.GameRuntime.Ecs.xml` 和 `Lumio.GameRuntime.Simulation.xml`。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）