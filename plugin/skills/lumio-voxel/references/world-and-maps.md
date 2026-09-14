# 世界、方块与底图

## 使用前

SDK 与工具的前置条件见 [开始开发](../../lumio-development/references/getting-started.md)，文件放置见 [项目结构](../../lumio-development/references/project-layout.md)，功能现状见 [能力说明](../../lumio-development/references/capabilities.md)，错误取证见 [诊断](../../lumio-development/references/diagnostics.md)。本指南解释 SDK 消费方法，不要求阅读私有实现。

核对日期：2026-09-14。公开样例版本为 `LumioSample b236d2e`。代码中存在接口只说明有消费入口；本文没有据此声称真实服务器、浏览器或冷恢复已经跑通。请以所用 SDK 包的 XML 文档、`content/docs/public-api.md`、`content/docs/error-codes.md` 和实际 Host 能力为准。

## 用什么表示游戏物体

| 物体 | 放在哪里 | 玩法后果 |
| --- | --- | --- |
| 地板、岩壁、普通建材 | 体素 | 格子保存方块身份，支持地形查询和破坏 |
| 玩家、掉落矿石、移动物体 | Entity | 位置、逻辑与同步归实体 |
| 有库存的固定箱子、有剩余储量的矿脉 | 体素 + Entity，稀疏绑定 | 格子负责占位，实体保存业务状态；破坏时协调处理两半 |
| 挖掘火花、选格提示 | 客户端 Local Entity | 从玩法结果产生表现，不成为服务端权威物体 |

不要把背包、阵营、矿脉剩余次数或脚本塞入 `BlockId`，也不要为每个普通地形格都造实体。BlockId、材质和具体模型来自项目目录及其配表；透明外观不自动意味着可穿过，编号大小也不能推出碰撞性质。

## 格子和区域身份

Section 是 `16 × 16 × 16` 的数据单元，包含 4096 格；Chunk 是 16 个 Section 竖向组合的列。把局部修订、加载状态和读写请求落到 Section 上。

当前 C# 游戏消费口把 Section 标识作为 `ulong sectionKey` 传入，把格内位置作为 `int cellOffset` 传入。取得这两个值应使用项目已有的地图/坐标映射或 SDK 对应接口，不要把字符串键、网络标识或自编的位打包直接转换成这个整数。SDK 未给出转换函数时，应向交付方取得映射说明，不发明一个 `WorldToSectionKey` API。

`cellOffset` 范围是 `0..4095`。当前格内序为 X 最快、其次 Z、最后 Y：对于已校验为 `0..15` 的局部坐标，`cellOffset = localY * 256 + localZ * 16 + localX`。世界连续坐标、整数格坐标与格内坐标是不同输入；负坐标不能用朝零截断代替项目的格定位规则。

注意版本宽度：这里核对到的 `VoxelCellQuery.BlockId` 和 `VoxelWriteEntry.BlockId` 是 `ushort`。不能因此断言底层所有 BlockId 都是 16 位；需要更大编号或更多状态位时，先核对 SDK 是否提供相应消费面，禁止截断强转。

## 从现成地图开始

公开 Sample 提供：

- `maps/sample.voxel`：已捕获的底图数据，适合作为复用已有地图的起点。
- `maps/sample.layout.json`：作者时布局说明，不是 DS 每次启动执行的生成程序。
- `server.json`：底图与配置的 Host 配置样例，包含 `base_map_id`、`base_map_version`、`base_map_content_sha256`。

Sample 使用 `world_profile=runtime+voxel`、`durability=snapshot_only`。接入时保留所用 Host 支持的词表，把地图文件、版本与实际文件 SHA-256 配对。不要手改快照二进制，也不要只改 hash 字段来“修好”损坏文件。改地图需要从作者工具重新导出，并验证当前 SDK/Host 能读取。

当前公开 `integration/capture-basemap.mjs` 仍调用引擎侧作者工具；仅 clone Sample 不代表取得该工具。没有已交付的捕获工具时，可复用匹配版本的现成快照，或报告缺少作者工具。不要教公开用户 clone 私有引擎仓，也不要实现另一套快照编码器补洞。

## Host 接入应当提供什么

游戏通常接收 `IVoxelGameplayQueries`、`IVoxelGameplayWrites`、`IVoxelPhysicsQueries`。宿主负责世界生命周期、材质目录、地图恢复与 Tick 接线；游戏负责玩法。

`VoxelGameplay.CreateVoxelWorld(nint hostWorldHandle)` 的名字容易误导：它只包装非零的既有宿主 handle，不创建 Native 世界。仅包装 handle 没有绑定 ABI 时，`BindAdapter()` 会失败。具备宿主接入职责且已拿到兼容 ABI 时，才使用接受 `INativeVoxelAbi` 的重载。游戏技能不自行制造 handle、Native ABI 或第二个世界。

接入完成后验证一小块已加载区域：已知实体方块能读到、已知空格能读到、区域外查询保留缺块状态；然后按 [查询](queries.md) 与 [写入](mutations.md) 增加玩法。渲染、光照、网格或编辑器工具若未随当前 SDK 提供，应把能力缺口写清楚，不以接口声明推导出完整编辑体验。

## 可公开核对的样例

- [Sample 世界模型与环境现状](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/README.md)
- [地图布局](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/maps/sample.layout.json)
- [作者时捕获入口](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/integration/capture-basemap.mjs)
- [Host 配置样例](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/server.json)
