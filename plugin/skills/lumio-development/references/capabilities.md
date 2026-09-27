# 世界模型与能力入口

世界模型帮你决定一个游戏对象应该做成方块还是实体，以及玩法逻辑该放在哪里。

以玩家打开箱子、挖矿和捡矿为例：

1. 地面和箱子占据的格子是方块（体素，按格子存储的地形）。
2. 箱子的物品和开关状态需要服务器管理，因此另外有一个实体（带身份、组件和逻辑的游戏对象）。箱子方块保存一条指向这个实体的引用。
3. 玩家、矿脉和掉落矿石也是实体；组件（挂在实体上的一组数据和行为）保存它们各自的状态。
4. 玩家通过 GAS（挂在实体上的技能系统）挖矿、支付体力、进入冷却，再拾取矿石。技能、冷却和预测都走这套组件。
5. 只有客户端显示、服务器无需知道的对象可以是本地实体；它仍是实体，不是世界的第三种东西。

## 世界里只有两种东西

静态地形用方块；会动或需要服务器逻辑的对象用实体。不动但有逻辑的箱子同时需要方块和实体，分别承担占格和逻辑。Sample 的 [`Gameplay/EntityTypes/BoxEntity.cs`](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/EntityTypes/BoxEntity.cs) 和 `Gameplay/Components/Box/BoxComponent.cs` 展示箱子声明；声明与同步规则见 [实体与组件](../../lumio-gameplay/references/entities-and-components.md)。

## 按任务找入口

| 要做的事 | Sample 入口 | 接着读 |
| --- | --- | --- |
| 定义实体、组件和本地实体 | `Gameplay/EntityTypes/`、`Gameplay/Components/` | [实体与组件](../../lumio-gameplay/references/entities-and-components.md) |
| 同步字段、聊天与远程调用 | `Gameplay/Components/Chat/` | [同步与 RPC](../../lumio-gameplay/references/sync-and-rpc.md) |
| 挖矿、捡矿、效果和预测 | `Gameplay/Abilities/`、`Gameplay/Effects/` | [GAS 技能](../../lumio-gameplay/references/gas-abilities.md) |
| 安排每帧系统顺序 | `Gameplay/SampleMiningSystem.Server.cs` | [每帧顺序](../../lumio-gameplay/references/tick.md) |
| 地图、体素读写和物理查询 | `Server/Assets/Maps/` | [体素](../../lumio-voxel/SKILL.md) |
| 启动服务器、配置存档 | `Server/Config/Startup/server.json`、`Tools/launcher.mjs` | [服务器配置](../../lumio-server/references/setup.md) |
| 接入方块资产 | `Client/Assets/Blocks/`、`Tools/check-block-assets.mjs` | [美术](../../lumio-art/SKILL.md) |
| 修改玩法数值 | `Gameplay/Tables/`、`Server/Config/Tables/`、`Client/Config/Tables/` | [配表](../../lumio-config/SKILL.md) |

## 记录限制时怎么说

- **能力不存在**：发布物没有所需的公开类型或命令。
- **尚未接线**：已有声明，但项目没有把它接入实际运行流程。Sample 未展示的用法写“示例中尚未提供”。
- **缺运行环境**：缺少 Docker、发布物或其他启动必需项。
- **本次未验证**：本次没有执行相应命令或场景。

精确类型和方法查 [发布物参考](getting-started.md#查公开参考)，本次命令结果查 [验证记录](../../../VERIFICATION.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
