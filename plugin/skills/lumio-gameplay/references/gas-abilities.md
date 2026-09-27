# GAS 技能与效果

GAS（Gameplay Ability System，玩法技能系统）把技能的准入、消耗、预测和效果结算放在实体上的组件里。Sample 用挖矿和捡矿展示这条链；示例没有提供可直接套用的 Gameplay Tags API。

## 从玩家挖矿到捡矿

按下面的真实声明阅读一次完整操作：

1. `Gameplay/EntityTypes/PlayerEntity.cs` 给玩家挂 `AbilityComponent`、`AttributeComponent` 和 `EffectComponent`，并用 `[DeclareAttribute("Stamina", Persist = true)]`、`[DeclareAttribute("Ore", Persist = true)]` 声明两个属性。
2. `Gameplay/Abilities/MineAbility.cs` 声明 `[AbilityType(2u, Prediction = PredictionKind.LogicPredict, Cost = "Stamina")]`，输入类型是 `MineAbility.Input`，目标字段是 `TargetHex`。`CanActivate` 检查目标和距离，`Execute` 扣除 `Stamina` 或为最后一击排入地形操作；`Register()` 把类型注册到 `AbilityTypeCatalog`。
3. 不是最后一击时，`MineAbility.Execute` 直接减少 `Stamina` 和 `VeinReserveComponent.Remaining`，并设置冷却。最后一击只写入待结算记录并调用按端实现的 `OrderFinalDig`；地形结果回来后才由 `SampleMiningComponent.Settle` 处理体力、储量和掉落。
4. `Gameplay/Abilities/PickupAbility.cs` 声明 `[AbilityType(3u, Prediction = PredictionKind.AuthorityOnly)]`。服务器文件 `PickupAbility.Server.cs` 在 `ExecuteCore` 中读取 `OrePileComponent.Amount`，调用 `Effects.Apply<PickupOreEffect, PickupOreEffect.Parameters>`，再处理掉落实体生命周期。
5. `Gameplay/Effects/PickupOreEffect.cs` 声明 `[EffectType(TypeId = 10, Instant = true)]`。`Parameters.Amount` 是要增加的矿石量，`Apply(NetEntityId target, in Parameters parameters)` 在 `EffectSettlementContext` 中写入目标的 `Ore` 属性。

## 预测、回滚和玩家能看到什么

`MineAbility` 是 `PredictionKind.LogicPredict`。客户端和服务器执行同一份 `Execute`；客户端的 `MineAbility.Client.cs` 把最后一击暂存到 GAS 预测会话，因此玩家可以先看到洞和碰撞变化。GAS 负责记录未确认窗口、按权威结果纠正并重放；这段 Sample 代码没有自己维护 Undo 表。

预测视图遇到未加载的 Section 时，`MineAbility.ClassifyPredictedDig` 返回 `PredictedDigVerdict.AwaitAuthority`；未知不是空气，客户端不能凭猜测改变地形。权威拒绝时，不应扣费、掉矿或把本地特效当成功。

`PickupAbility` 明确是 `PredictionKind.AuthorityOnly`，所以拾取的 `PickupOreEffect` 由权威结算；Sample 没有提供客户端预测这个奖励 Effect 的实现。客户端最终应以权威属性同步和实体变化刷新 UI，真实的视觉反馈需要 Host 运行验证。

## 属性、效果与标签

- 属性是实体上的 `AttributeComponent` 字段。Sample 的 `Stamina` 和 `Ore` 由实体声明，初始值来自配置绑定；`MineAbility` 读取 `GetBaseValue`，`PickupOreEffect` 通过 `GetBase` 写入。
- 效果是可登记的结算类型。`PickupOreEffect.Register()` 调用 `EffectTypeCatalog.Register<PickupOreEffect, Parameters>`；生成的 `GeneratedEffectRegistry.g.cs` 可按类型返回 `10`。
- 技能有稳定类型号：Sample 的 `MoveAbility`、`MineAbility`、`PickupAbility` 分别登记为 `1`、`2`、`3`。不要因文件排序重编号。
- Sample `origin/main` 的 `Gameplay/` 没有 Gameplay Tags 或标签声明。需要标签时先查当前 SDK 的公开 XML/API；示例中尚未提供，不能编一个 `Tag` 类或方法。

服务器、客户端和体素接缝的边界分别见 [lumio-server](../../lumio-server/SKILL.md)、[lumio-client](../../lumio-client/SKILL.md) 和 [体素写入](../../lumio-voxel/references/mutations.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
