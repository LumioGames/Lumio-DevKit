# 实体与组件

实体（Entity）是有生命周期的玩法对象，组件（Component）保存实体的一组状态或行为。这一页先说明怎样把一个对象放进世界，再说明怎样按端实现它。

## 先看一个箱子

示例把箱子当作“格子占位 + 实体逻辑”，而不是把库存塞进方块编号。按这个例子写玩法：

1. 在 `Gameplay/EntityTypes/BoxEntity.cs` 声明 `BoxEntity`，使用 `[EntityType(Mode.CS)]`、`[BlockEntity]` 和 `[Has(typeof(BoxComponent))]`。
2. 在 `Gameplay/Components/Box/BoxComponent.cs` 声明 `[EcsComponent]` 的 `BoxComponent`。`Name` 和 `Locked` 使用 `Sync<T>` 与 `Scope.Aoi`，`Inventory` 使用 `SyncList<int>`、`Scope.Claim` 和 `claimBy: nameof(Openers)`，`Openers` 是 `Scope.None` 的 `SyncList<NetEntityId>`。
3. 在 `Gameplay/Components/Box/BoxComponent.Server.cs` 只让服务器实现 `Open(NetEntityId opener)` 和 `Close(NetEntityId opener)`，通过增删 `Openers` 改变谁能看到库存。
4. 让体素绑定表保存箱子占的格子，让 `BoxComponent` 保存名字、锁和库存。服务器重启后 `Openers` 不在网络和存档中，箱子从关闭状态开始。

## 选择实体类型

Sample `origin/main` 中的声明可以作为对照：

| 需要的对象 | 声明 | 说明 |
| --- | --- | --- |
| 玩家 | `Gameplay/EntityTypes/PlayerEntity.cs` 的 `PlayerEntity`、`[EntityType(Mode.CS)]` | 同时挂 `ObserverComponent`、`LogicTransform`、`AbilityComponent`、`AttributeComponent`、`EffectComponent` 等组件。 |
| 掉落矿石 | `Gameplay/EntityTypes/OreDropEntity.cs` 的 `OreDropEntity`、`[EntityType(Mode.CS)]` | 有生命周期和位置，挂 `OrePileComponent`。 |
| 只在客户端显示的火花 | `Gameplay/EntityTypes/MiningSparkEntity.Client.cs` 的 `MiningSparkEntity`、`[EntityType(Mode.Local)]` | 服务器编译排除该文件，不进入网络和存档。 |
| 不动但有储量的矿脉 | `Gameplay/EntityTypes/VeinEntity.cs` 的 `VeinEntity`、`[EntityType(Mode.CS)]`、`[BlockEntity]` | 格子位置在绑定表，`VeinReserveComponent.Remaining` 保存实体上的储量。 |

声明类保持 `abstract` 且不放业务成员；通过 `[Has]` 列出组件。一个组件可用共享声明加端后缀实现：`BoxComponent.cs` 是双端声明，`BoxComponent.Server.cs` 只放服务器方法。`[Persist]` 表示字段进入存档，是否上网仍由字段的 `Scope` 决定。

## 方块实体的边界

`BoxEntity` 和 `VeinEntity` 都有 `[BlockEntity]`。格子负责静态占位，实体负责库存或储量等逻辑；不要在实体里另存一份格子坐标，也不要给普通地形格逐格创建实体。需要移动、观察或掉落的对象使用普通 `Mode.CS` 实体；只服务客户端画面的对象使用 `Mode.Local`。

如果一个能力没有在 Sample 的声明和生成结果中出现，写“示例中尚未提供”，不要根据类名猜接口。体素读写和绑定提交请接着读 [体素世界](../../lumio-voxel/references/world-and-maps.md) 与 [写入](../../lumio-voxel/references/mutations.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
