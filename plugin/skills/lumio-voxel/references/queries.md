# 读取与地形物理查询

地形查询回答“这一格是什么”或“这一步能走多远”，让玩法在已有世界数据上做判断。

## 用移动和挖矿看一次查询

1. 玩家准备向前走，`MoveAbility` 用一个盒子沿位移扫过地形。
2. 查询返回允许走到的位置；碰到墙时减少行程。
3. 玩家挖矿前，客户端查矿脉所在区域与格子。
4. 格子数据尚未收到时等待服务器结果，不能把它当空气挖穿。

先满足 [世界与地图](world-and-maps.md) 的环境条件。GAS（挂在实体上的技能系统）如何接收输入见 [GAS 技能](../../lumio-gameplay/references/gas-abilities.md)。

## 读取格子

[Gameplay/SampleMiningComponent.Client.cs](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/SampleMiningComponent.Client.cs) 用 `VoxelGameplayBinding.Resolve` 获取本端适配器，再经 `TryReadSectionBindings` 查本端收到的绑定表。定位不到只说明当前不知道位置。

以下原文摘自 `Gameplay/Abilities/MineAbility.Client.cs`，提交 `f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb`，Apache-2.0：

```csharp
        VoxelCellQuery read = resolved.Read(section, offset);
        PredictedDigVerdict verdict = ClassifyPredictedDig(true, read.HasBlockId, read.BlockId,
            read.HasBlockId ? resolved.BindingGet(section, offset) : null, reserve.Entity.ToHex());
```

`HasBlockId` 为真才能使用读值。`BlockId` 是 `uint`；`SectionRevision` 是这次读取对应的区域修订，写入时用来检查区域是否已经改变。写入步骤见 [挖穿](mutations.md)。

## 移动扫掠

[Gameplay/Abilities/MoveAbility.cs](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Abilities/MoveAbility.cs) 的 `CanActivate` 先取得 `IAbilityPhysicsPort`，从配表读取步长和半径，再检查位置、位移与半径有效。实际调用原文如下，同样核对于 `f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb`，Apache-2.0：

```csharp
        AbilitySweepHit hit = physics.SweepBox(origin, displacement, new Vector3(radius));
```

这里用 AABB（与坐标轴对齐的盒子）表示角色查询形状。Sample 接着检查 `TravelFraction` 的范围、是否完整通过以及 `Point` 是否与下一位置一致；无效结果会保留错误，不能假装查询成功。

`physics_unavailable` 表示缺物理端口，`physics_invalid_query` 表示输入无效；缺区域等拒绝原因按 [错误码](../../lumio-development/references/diagnostics.md#按症状查错误码) 处理。不要安装空查询实现，或捕获全部异常后当作没有墙。

## 核对效果

在相同地图上分别走空地、走向墙体、查询尚未收到的区域；空地应能走、墙体应限制行程、未知区域应保留等待或拒绝结果。对照服务器状态与客户端画面，移动和冷却仍通过 GAS 执行。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
