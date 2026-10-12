# GAS 技能与效果

GAS（Gameplay Ability System，玩法技能系统）通过实体上的组件统一处理技能准入、冷却、属性变化、效果与预测。

## 从挖矿到捡矿

1. 玩家实体 `Gameplay/EntityTypes/PlayerEntity.cs` 挂上 `AbilityComponent`（技能）、`AttributeComponent`（数值属性）、`EffectComponent`（效果），并声明会保存的 `Stamina`（体力）与 `Ore`（矿石）属性。
2. `Gameplay/SampleGameplay.cs` 的 `BindPlayer` 把挖矿的体力检查接到玩家现有属性。只有 `MineAbility` 支付挖矿体力；走路与拾取没有该消耗，体力耗尽后仍能捡矿。
3. `Gameplay/Abilities/MineAbility.cs` 用 `MineAbility.Input.TargetHex` 指定矿脉。`CanActivate` 检查实体还存在、类型为 `VeinEntity`、仍有储量与有效绑定，并检查距离；GAS 同时负责冷却和消耗准入。
4. 普通一击在 `Execute` 中扣体力、减少 `VeinReserveComponent.Remaining`，然后设置冷却。最后一击调用按端实现的 `OrderFinalDig`；服务器的 `MineAbility.Server.cs` 转到 `SampleMiningComponent.StageFinal`，排入地形修改，并把等待信息写到玩家的 `PendingDigComponent`。
5. 地形真正应用后，`Gameplay/SampleMiningComponent.Server.cs` 的 `Settle` 在后续业务阶段读取结果，再由 `Pay` 扣体力、处理仍存活的矿脉储量，并通过 `World.Commands.Create<OreDropEntity>()` 排入掉落。地形请求若被拒绝，不扣体力、不发矿。排入成功时已设置的冷却与最终地形结果是两件事。
6. `Gameplay/Abilities/PickupAbility.cs` 检查掉落还存在、`OrePileComponent.Amount` 大于零、玩家在拾取距离内。`PickupAbility.Server.cs` 的 `ExecuteCore` 先取出数量，再把矿堆数量清零，防止同一帧第二个人重复领取；随后调用 `Effects.Apply<PickupOreEffect, PickupOreEffect.Parameters>` 并排入销毁掉落实体。
7. `Gameplay/Effects/PickupOreEffect.cs` 的 `PickupOreEffect` 是即时效果。引擎提交实体创建/销毁后结算这个效果，`Apply` 在 `EffectSettlementContext`（引擎允许写效果属性的结算上下文）中把 `Parameters.Amount` 加到玩家 `Ore` 的基础值。最终玩家看到掉落消失、矿石数量增加。

挖矿声明摘自 [`Gameplay/Abilities/MineAbility.cs`](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Abilities/MineAbility.cs)，提交 `f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb`，许可证 Apache-2.0：

```csharp
[AbilityType(2u, Prediction = PredictionKind.LogicPredict, Cost = "Stamina")]
public sealed partial class MineAbility : AbilityType<MineAbility.Input>
```

## 预测与回滚时看到什么

预测（服务器结果到达前，客户端先执行允许预测的逻辑）让挖矿立即响应。`MineAbility` 使用 `PredictionKind.LogicPredict`，两端执行相同的 `Execute`，最后一击的端实现不同：

1. `Gameplay/SampleMiningComponent.Client.cs` 的 `TryLocate` 从客户端已收到的绑定副本查找格子；客户端不创建或绑定矿脉。
2. `Gameplay/Abilities/MineAbility.Client.cs` 读取该格子的预测视图。仍有方块且绑定目标正确时，把挖掘排进 GAS 预测会话，玩家可先看到洞，碰撞查询也使用挖后的结果。
3. 服务器确认后，客户端保留确认的结果。服务器结果不同或拒绝时，GAS 回滚（撤销未被确认的预测变化），再重放（基于服务器结果重新执行仍待确认的输入）。玩家可能看到方块和碰撞恢复，随后未确认的动作重新表现；不要在游戏代码里再维护一张撤销表。
4. Section（地图分块）未加载、尚无绑定位置或没有打开预测会话时，客户端等待服务器，不凭空挖洞。`ClassifyPredictedDig` 区分 `Order`、`AwaitAuthority`、`Refuse`：未知不等于空气，也不等于已证明超出距离。

`PickupAbility` 使用 `PredictionKind.AuthorityOnly`（只由服务器执行）。玩家的奖励效果等服务器结算后再同步；预测拾取奖励的示例中尚未提供。回滚也不会把“本地看见洞”变成“服务器已经发矿”。

## 怎样组织技能、属性、效果和标签

| 内容 | Sample 用法 | 修改时检查 |
| --- | --- | --- |
| 技能 | `MoveAbility`、`MineAbility`、`PickupAbility` 的稳定类型号分别为 `1`、`2`、`3`。 | 通过 GAS 激活，不从普通系统直接调用 `Execute` 绕过准入与冷却。 |
| 属性 | `Stamina`、`Ore` 由玩家声明，初始值来自配置。`GetBaseValue` 读基础值，挖矿用 `SetBaseValue` 扣体力。 | 使用当前世界的 `SampleConfigBinding`，不要另建一份库存或体力计数。 |
| 效果 | `PickupOreEffect` 为 `[EffectType(TypeId = 10, Instant = true)]`；`Parameters.Amount` 传入奖励。 | `Effects.Apply` 排入效果；不要从拾取代码直接调用效果的 `Apply` 绕过结算。 |
| 标签（用于表示或匹配玩法状态的标记） | Gameplay Tags 的声明和使用示例中尚未提供。 | 先查安装版本的公开 API 参考，不能凭概念编造 `Tag` 类型、阻止规则或调用签名。 |

`GeneratedAbilityRegistry.RegisterAll()` 登记技能；效果则由 `Gameplay/SampleGameplay.cs` 的 `RegisterCatalog` 调用 `PickupOreEffect.Register()` 登记。`GeneratedEffectRegistry` 提供类型号查找，不能把它当作效果登记已经完成的证据。生成步骤见 [代码生成](code-generation.md)。

失败时沿流程定位：挖不了先看目标、绑定、距离、体力和冷却；最后一击无奖励按事务号对照 `mining_stage`、`mining_applied`、`mining_reward` 或 `mining_refused` 日志；捡不到检查 `pickup_invalid_target`、`pickup_target_gone`、`pickup_out_of_reach`。帧内顺序见 [Tick](tick.md)，宿主日志见 [服务器技能](../../lumio-server/SKILL.md)，地形处理见 [体素写入](../../lumio-voxel/references/mutations.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）