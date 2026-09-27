# 世界、方块与底图

## 使用前

SDK 与工具的前置条件见 [开始开发](../../lumio-development/references/getting-started.md)，文件放置见 [项目结构](../../lumio-development/references/project-layout.md)，功能现状见 [能力说明](../../lumio-development/references/capabilities.md)，错误取证见 [诊断](../../lumio-development/references/diagnostics.md)。本指南解释 SDK 消费方法，不要求阅读私有实现。

核对基线为 `LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb` 与 Engine v0.0.2。代码中存在接口只说明有消费入口；真实服务器、浏览器或冷恢复仍须用同一发布物验证。公开 API、错误码和 XML 说明以 `Engine/sdk/` 中随包内容为准。

## 用什么表示游戏物体

| 物体 | 放在哪里 | 玩法后果 |
| --- | --- | --- |
| 地板、岩壁、普通建材 | 体素 | 格子保存方块身份，支持地形查询和破坏 |
| 玩家、掉落矿石、移动物体 | Entity | 位置、逻辑与同步归实体 |
| 有库存的固定箱子、有剩余储量的矿脉 | 体素 + Entity，稀疏绑定 | 格子负责占位，实体保存业务状态；破坏时协调处理两半 |
| 挖掘火花、选格提示 | 客户端 Local Entity | 从玩法结果产生表现，不成为服务端权威物体 |

不要把背包、阵营、矿脉剩余次数或脚本塞入 `BlockId`，也不要为每个普通地形格都造实体。`BlockId` 是无符号 `uint`；材质和具体模型来自项目目录及其配表。透明外观不自动意味着可穿过，编号大小也不能推出碰撞性质。

## 格子和区域身份

Section 是 `16 × 16 × 16` 的数据单元，包含 4096 格；Chunk 是 16 个 Section 竖向组合的列。把局部修订、加载状态和读写请求落到 Section 上。

当前 C# 游戏消费口把 Section 标识作为 `ulong sectionKey` 传入，把格内位置作为 `int cellOffset` 传入。取得这两个值应使用项目已有的地图/坐标映射或 SDK 对应接口，不要把字符串键、网络标识或自编的位打包直接转换成这个整数。SDK 未给出转换函数时，应向交付方取得映射说明，不发明一个 `WorldToSectionKey` API。

`cellOffset` 范围是 `0..4095`。当前格内序为 X 最快、其次 Z、最后 Y：对于已校验为 `0..15` 的局部坐标，`cellOffset = localY * 256 + localZ * 16 + localX`。世界连续坐标、整数格坐标与格内坐标是不同输入；负坐标不能用朝零截断代替项目的格定位规则。

`VoxelCellQuery.BlockId` 与 `VoxelWriteEntry.BlockId` 均按 `uint` 处理；未知/未就绪结果没有可用的方块值。

## 从现成地图开始

公开 Sample 提供：

- `Server/Assets/Maps/sample.voxel`：已捕获的底图数据，适合作为复用已有地图的起点。
- `Server/Assets/Maps/sample.layout.json`：作者时布局说明，不是 DS 每次启动执行的生成程序。
- `Server/Config/Startup/server.json`：底图与配置的 Host 模板，包含 `base_map_id`、`base_map_version`、`base_map_content_sha256`。

Sample 使用 `world_profile=runtime+voxel`、`durability=snapshot_only`。接入时保留所用 Host 支持的词表，把地图文件、版本与实际文件 SHA-256 配对。不要手改快照二进制，也不要只改 hash 字段来“修好”损坏文件。改地图需要从作者工具重新导出，并验证当前 SDK/Host 能读取。

作者时捕获入口为 `Tools/capture-basemap.mjs`；仅 clone Sample 不代表取得作者时工具的全部构建依赖。没有工具时，可复用匹配版本的现成快照，或报告缺少工具。不要实现另一套快照编码器补洞。

## Host 接入应当提供什么

游戏通常接收 `HostVoxelWorldAdapter` 的读取、写入和 Section 绑定能力。宿主负责世界生命周期、材质目录、地图恢复与 Tick 接线；游戏负责玩法。通过 `VoxelGameplayBinding.Resolve(world.Manager)` 取得已绑定的适配器，玩法不自行制造 handle、Native ABI 或第二个世界。

方块实体的关联只来自 Section 绑定表：一格保存体素，占格的业务数据保存在实体；客户端看到的范围跟随持有该 Section 的订阅，而不是另造一套空间 AOI。箱子示例见 `Gameplay/EntityTypes/BoxEntity.cs` 和 `Gameplay/Components/Box/BoxComponent.cs`。

接入完成后验证一小块已加载区域：已知实体方块能读到、已知空格能读到、区域外查询保留缺块状态；然后按 [查询](queries.md) 与 [写入](mutations.md) 增加玩法。渲染、光照、网格或编辑器工具若未随当前 SDK 提供，应把能力缺口写清楚，不以接口声明推导出完整编辑体验。

## 可公开核对的样例

- [Sample 世界模型与环境现状](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/README.md)
- [地图布局](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Server/Assets/Maps/sample.layout.json)
- [作者时捕获入口](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Tools/capture-basemap.mjs)
- [Host 配置样例](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Server/Config/Startup/server.json)

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
