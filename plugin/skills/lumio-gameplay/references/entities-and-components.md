# 实体与组件

实体（Entity，有身份和生命周期的对象）与组件（Component，挂在对象上的状态或行为）用来表达玩家、掉落物、箱子等玩法对象。

## 先看一个箱子

1. 箱子占住一个格子：格子保存方块（体素）的类型，不保存库存。
2. `Gameplay/EntityTypes/BoxEntity.cs` 声明箱子的逻辑实体，`[Has(typeof(BoxComponent))]` 给它挂上组件。格子通过绑定表中的引用找到这个实体。
3. `Gameplay/Components/Box/BoxComponent.cs` 保存箱子的名字、锁和库存。附近玩家能看到名字和锁；服务器在 `BoxComponent.Server.cs` 调用 `Open(NetEntityId opener)` 后，指定玩家才能收到库存。
4. `Close(NetEntityId opener)` 移除该玩家的查看资格。当前开箱者不进存档，因此重启后所有人都需要重新打开箱子。

箱子的类型声明摘自 [`Gameplay/EntityTypes/BoxEntity.cs`](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/EntityTypes/BoxEntity.cs)，提交 `f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb`，许可证 Apache-2.0：

```csharp
[EntityType(Mode.CS)]
[BlockEntity]
[Has(typeof(BoxComponent))]
public abstract class BoxEntity
{
}
```

## 先选对象，再写组件

世界中只有方块和实体。静态地形用方块；会动或需要服务器逻辑的对象用实体；只有客户端画面、服务器无需知道的对象用本地实体。箱子属于方块实体：格子负责占位，实体负责逻辑，两者靠引用相连。

| 对象 | Sample 声明位置 | 组件与位置来源 |
| --- | --- | --- |
| 玩家 | `Gameplay/EntityTypes/PlayerEntity.cs`：`Mode.CS`（服务器与客户端都有） | `LogicTransform` 保存逻辑位置，`ObserverComponent` 参与观察与连接，`AbilityComponent`、`AttributeComponent`、`EffectComponent` 承载 GAS（玩法技能系统）。 |
| 掉落矿石 | `Gameplay/EntityTypes/OreDropEntity.cs`：`Mode.CS` | `LogicTransform` 保存位置，`OrePileComponent` 保存数量；不占地形格。 |
| 本地火花 | `Gameplay/EntityTypes/MiningSparkEntity.Client.cs`：`Mode.Local`（仅客户端存在） | `MiningSparkComponent` 是本地标记，不上网、不进存档。 |
| 矿脉 | `Gameplay/EntityTypes/VeinEntity.cs`：`Mode.CS` 加 `[BlockEntity]` | 位置来自格子的绑定表，`VeinReserveComponent.Remaining` 保存剩余挖掘次数。 |

实体声明保持 `abstract` 且不放业务成员，用 `[Has]` 组合组件。组件以 `[EcsComponent]` 声明并继承 `Component`；`BoxComponent` 的共享声明保存字段，服务器方法放在同名 `.Server.cs`。文件拆分规则见 [同步与 RPC](sync-and-rpc.md)。

`[Persist]` 表示字段进入存档；同步范围由 `Scope`（哪些客户端能收到）决定。箱子的 `Name`、`Locked`、`Inventory` 都保存，`Openers` 不保存。技能、冷却和预测交给实体上的 GAS 组件，见 [GAS 技能](gas-abilities.md)。

## 方块实体怎么接入

`BoxEntity`、`VeinEntity` 不挂位置组件，也不在组件中另存一份当前格子坐标。体素绑定表连接格子和逻辑实体；普通地形无需逐格创建实体。实际绑定流程以 Sample 已接好的矿脉为例，见 [体素世界](../../lumio-voxel/references/world-and-maps.md) 与 [体素写入](../../lumio-voxel/references/mutations.md)。

箱子目前提供声明、开关方法和对象级测试，场景里的放箱、点击开箱与库存界面尚未接线；完整可操作的箱子示例中尚未提供。`MiningSparkEntity` 也只有类型与空标记组件，创建火花、渲染和自动消失的流程示例中尚未提供。不要把这些声明当成已显示出来的玩法。

新增对象后按 [代码生成](code-generation.md) 构建两端，检查注册表包含实体及组件。若服务器出现本地火花类型，先查端后缀和构建参数；若箱子位置不同步，先查格子绑定与 Section（地图分块）订阅，不要补第二套坐标字段。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）