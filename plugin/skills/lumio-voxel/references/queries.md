# 读取与地形物理查询

先确认已满足 [世界与地图](world-and-maps.md) 的 Host 前置条件。本页按 Engine v0.0.2 核对；以下示例只使用公开 SDK 消费面。

## 读格子：只使用 Sample 已接线的读法

公开 Sample 的客户端反向定位在 [`Gameplay/SampleMiningComponent.Client.cs`](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/SampleMiningComponent.Client.cs)。它通过 `VoxelGameplayBinding.Resolve(World.Manager)` 取得适配器，再调用 `TryReadSectionBindings`；定位不到时返回 `false`，不把“本端尚未收到 Section”当作没有绑定。挖矿的实际格子读取也只使用 `HostVoxelWorldAdapter.Read`，再检查 `VoxelCellQuery.HasBlockId`、`BlockId` 和 `SectionRevision`。

客户端挖矿代码中的真实读取片段如下（[`Gameplay/Abilities/MineAbility.Client.cs`](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Abilities/MineAbility.Client.cs)）：

```csharp
VoxelCellQuery read = resolved.Read(section, offset);
PredictedDigVerdict verdict = ClassifyPredictedDig(true, read.HasBlockId, read.BlockId,
    read.HasBlockId ? resolved.BindingGet(section, offset) : null, reserve.Entity.ToHex());
```

没有 `HasBlockId` 时，Sample 不把 `BlockId` 当作有效结果；`SectionRevision` 只作为同一读值对应的并发身份传回排入调用。缺数据时等待后续接线，不清空世界、不把未知填成空气，也不凭另一个未经核对的读路径覆盖结果。SDK 还有其它体素查询类型时，以当前 Engine XML 为准；本页不编写 Sample 没有展示的 `IVoxelGameplayQueries` 或批量读取签名。

## 查询形状与结果

Sample 已公开的物理接缝在 [`Gameplay/Abilities/MoveAbility.cs`](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Abilities/MoveAbility.cs)：`MoveAbility.CanActivate` 先取得 `IAbilityPhysicsPort`，再用配置中的半径调用 `SweepBox`。以下是该文件的实际片段：

```csharp
if (owner.Physics is not IAbilityPhysicsPort physics)
{
    failureCode = "physics_unavailable";
    return false;
}
float step = (float)SampleConfigBinding.For(owner.World).Movement.StepMeters;
float radius = (float)SampleConfigBinding.For(owner.World).Movement.SweepRadiusMeters;
LogicTransform logic = owner.Get<LogicTransform>();
Vector3 origin = logic.LocalPosition;
Vector3 displacement = new(input.Dx * step, 0f, input.Dz * step);
AbilitySweepHit hit = physics.SweepBox(origin, displacement, new Vector3(radius));
```

随后 Sample 检查 `AbilitySweepHit.TravelFraction` 是否为有限的 `0..1`、未碰撞时是否为完整行程，并检查 `Point` 与计算出的下一位置一致；不一致会保留故障而不是当作未命中。盒体输入必须来自有限的 `LogicTransform`、配置半径和有效位移。角色等实体碰撞仍由 ECS/Runtime 侧处理，玩法不要安装空物理端口或捕获所有异常。

`Unresolved`、`physics_unavailable`、`physics_invalid_query`、`physics_shape_unsupported` 等具体错误以 Engine v0.0.2 公共 XML/错误码参考为准；查询未能回答时不能把它当 `Miss`、`Hit` 或空气。查询本身也不等于请求加载，交给 Host 的驻留策略后在后续时机再尝试。

## 接到 GAS 移动前先核对形状

Sample 通过 `IAbilityPhysicsPort` 的 `SweepBox(origin, displacement, new Vector3(radius))` 走 GAS 的 AABB 扫掠入口；Engine v0.0.2 的 Runtime Host 负责把真实体素适配器绑定到 Ability 组件。玩法不安装空实现或自行捕获所有异常。

`SweepBox` 的结果可能是已命中、未命中或由 `AbilityPhysicsRejectedException` 明确拒绝。`physics_unavailable`、`physics_unresolved`、`physics_invalid_query` 与 `physics_shape_unsupported` 需要保留原码；未知地形不得伪装成未命中。第五步准入失败发生在扣费、冷却和执行条目之前，普通业务拒绝只结束这一次移动。

## 如何确认接通

至少观察：已加载空地完整通过、已加载墙体限制行程、未就绪区域拒绝当前查询、无效形状保留具体错误。同一场景分别确认 Server 与 Client Replica 使用正确世界。测试端口只证明游戏分支，真实地形效果需相应 Native/Host 运行证据，记录 SDK 身份、地图版本、操作和查询结果。

公开阅读入口：[Sample 移动技能](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Abilities/MoveAbility.cs)、[服务端 Host 绑定说明](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/SampleGameplay.Server.cs)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
