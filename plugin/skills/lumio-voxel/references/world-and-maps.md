# 世界、方块与底图

方块负责静态地形，实体负责会动或需要逻辑的东西，底图提供世界启动时的地形。

## 用箱子理解分工

1. 箱子占据的格子是方块。
2. 箱子的库存放在 `BoxComponent`，由 `BoxEntity` 携带。
3. 格子与实体通过一条引用相连；箱子不需要第二份位置。
4. 客户端显示箱子外观，玩家请求取放物品时由服务器处理逻辑。

世界只有方块（体素）与实体。只供客户端画面的火花是本地实体，不是第三种世界对象。声明与同步规则见 [实体与组件](../../lumio-gameplay/references/entities-and-components.md)，真实箱子声明在 [Gameplay/EntityTypes/BoxEntity.cs](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/EntityTypes/BoxEntity.cs)。

## 方块编号与区域

`BlockId` 是 `uint`（32 位无符号整数）。发布包的 `VoxelCellQuery` 读值和 `VoxelWriteEntry` 写值都使用这个类型；不要缩成 `ushort`。编号用于标识方块，不存库存、储量或脚本。外观透明也不代表可以穿过，碰撞和外观分别由方块目录与资产描述决定。

Section（16 × 16 × 16 格的地形区域）是 Sample 查询、修订与订阅使用的单位。`sectionKey` 标识区域，`cellOffset` 标识其中一格。先用 Sample 已有位置查询取得它们，再调用读写接口。矿脉定位入口是 `SampleMiningComponent.TryLocate`，见 [查询](queries.md)。

## 使用现成地图

| Sample 路径 | 用途 |
| --- | --- |
| `Server/Assets/Maps/sample.voxel` | DS 可恢复的底图文件。 |
| `Server/Assets/Maps/sample.layout.json` | 制作底图时使用的布局说明。 |
| `Server/Assets/Maps/official-catalog.json` | 方块种类、形状与美术资源引用。 |
| `Server/Config/Startup/server.json` | 地图路径、编号、版本、哈希与存档目录。 |

先按 [服务器搭建](../../lumio-server/references/setup.md) 跑现成地图。换地图时同时核对配置指向的文件和身份，使用匹配的方块目录。检查点恢复沿用原目录；不要手改二进制或哈希来绕过加载错误。

## 当前制作能力

[Tools/capture-basemap.mjs](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Tools/capture-basemap.mjs) 是制作底图的脚本入口，但它需要 `Engine/tools/capture-voxel.mjs`。v0.0.2 发布物没有这个工具，因此当前发布物不能通过这条脚本重新捕获底图；这是缺少已发布工具，不是现成地图无法运行。地图制作工具需由上游补齐。

读取、移动扫掠和挖穿已有 Sample 调用，见 [查询](queries.md) 与 [写入](mutations.md)。方块材质和 WebGL2 已有接入，见 [世界资产](../../lumio-art/references/world-assets.md)。通用建造技能在示例中尚未提供。

源码入口：[地图目录](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Server/Assets/Maps/official-catalog.json)、[客户端矿脉定位](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/SampleMiningComponent.Client.cs)。环境前置见 [开始开发](../../lumio-development/references/getting-started.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
