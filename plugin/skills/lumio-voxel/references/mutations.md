# 建造、破坏与挖穿

体素写入把玩法决定变成地形变化，并把最终结果交回玩法结算。

## 用挖穿矿脉看顺序

1. 玩家挖矿，技能检查目标、距离、体力和储量。
2. 最后一击先读取目标格与区域修订，再排入挖穿请求。
3. Runtime（每帧推进世界的运行时）应用地形变化并处理绑定。
4. Sample 读取实际结果后结算，产生掉落；客户端再显示更新。

技能与结算整体见 [GAS 技能](../../lumio-gameplay/references/gas-abilities.md)，执行阶段见 [每帧顺序](../../lumio-gameplay/references/tick.md)。本页只解释地形读写部分。

## 用读到的修订排入操作

先按 [查询](queries.md) 获取目标格。`Staged` 只表示请求已经排入，不能当作地形已改变。

以下原文摘自 `Gameplay/SampleMiningComponent.Server.cs`，提交 `f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb`，Apache-2.0：

```csharp
        VoxelStageResult result = adapter.TryStageCoalescibleDigThrough(sectionKey, cellOffset,
            cell.SectionRevision, transaction);
```

`MineAbility.Server.cs` 调用 `SampleMiningComponent.StageFinal` 进入这条路径。Sample 把待处理记录放在 `PendingDigComponent`，后续根据实际结果结算，而不是刚排入就奖励矿石。

## 客户端预测仍走 GAS

以下原文摘自 `Gameplay/Abilities/MineAbility.Client.cs`，提交 `f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb`，Apache-2.0：

```csharp
        VoxelStageResult result = adapter!.TryStageDigThrough(sectionKey, cellOffset, cell.SectionRevision, transaction);
        ordered = result.Status == VoxelStageStatus.Staged;
```

客户端只有在本端已知区域、格子与绑定时才排入预测。未知数据等待服务器结果；预测洞的保留、纠正与重放交给 GAS，游戏不另写一套撤销记录。

## 处理失败与验证

格子修订变化后重新读取并重新判断条件，不用新修订盲目重放旧扣费。普通目标无效、距离不足或缺体力只影响这次操作；底层故障保留具体错误。

核对时查看 `mining_stage`、`mining_applied`、`mining_refused`，以及格子、绑定、实体、掉落和库存。两个玩家争同一矿脉时，确认没有重复奖励；若要确认可保存，再运行导览第十四步恢复验证。

通用的“放置建材”技能在示例中尚未提供，不能把这段挖穿接口当成完整建造 API。箱子的格子和逻辑如何配合见 [实体与组件](../../lumio-gameplay/references/entities-and-components.md)。

源码入口：[服务端排入与结算](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/SampleMiningComponent.Server.cs)、[服务端技能分支](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Abilities/MineAbility.Server.cs)、[客户端预测分支](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Abilities/MineAbility.Client.cs)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
