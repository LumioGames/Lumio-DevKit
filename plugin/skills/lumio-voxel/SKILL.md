---
name: lumio-voxel
description: 使用 Lumio 已有体素 API 制作地形、建造、挖掘与地形查询玩法，处理缺块、修订冲突和体素/实体协作；不用于实现 Native 体素内核、网格算法或存储格式。
---

# Lumio 体素玩法

把游戏需求接到已交付 SDK 的体素读取、物理查询和写入端口，完成一个能观察成功与拒绝结果的玩法切片。只读取当前任务需要的参考页。

## 任务路由

| 用户要做什么 | 阅读 |
| --- | --- |
| 地图、方块、矿脉或箱子该怎样建模；加载现成底图 | [世界与地图](references/world-and-maps.md) |
| 选格、射线、移动扫掠、区域查询、缺块时怎么办 | [读取与物理查询](references/queries.md) |
| 放置、破坏、挖穿、绑定实体与掉落 | [写入与玩法提交](references/mutations.md) |

SDK 获取、项目结构、可用能力和故障证据统一从 [公共入口](references/world-and-maps.md#使用前) 进入，不要求开发者取得引擎源码权限。

## 执行方式

1. 确认游戏要影响的格子、Role、业务实体与成功结果；使用项目已经注入的端口。
2. 核对 `Engine/manifest.json` 的版本和 SDK 随附的公开签名。本文按 `LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb` 与 Engine v0.0.2 编写。
3. 在一个小区域实现操作：先读可用性与修订，再做玩法判断，最后提交结构化写入。
4. 观察权威结果和客户端结果；代码编译、测试替身通过、真实 Host 运行分别报告。

## 关键约束

- 地形在体素上；库存、储量、掉落、角色逻辑在实体上。静态物体需要逻辑时用体素与实体的稀疏绑定。
- `Pending`、`Unavailable` 与物理 `Unresolved` 都不能当空气。普通操作被拒绝只拒绝这次操作；SDK 错误要保留原因。
- 玩法提交意图，由 Runtime 在 Tick 提交阶段应用；得到 `CommitId` 尚不等于已生效。
- Server 权威和 Client Replica 使用各自的世界；Local 模式也不共享一份可变体素数据。
- 物理查询的具体类型和参数以 Engine v0.0.2 随附 XML 为准；Sample 的移动技能实际使用宿主绑定的 `IAbilityPhysicsPort.SweepBox`，不要从未展示的接口名猜测另一套接线。
- 查询、写入和预测都必须使用 Engine v0.0.2 提供的真实宿主接线。接口声明或局部测试不能替代 DS/Client 的运行证据；缺运行环境时标记为 `BLOCKED_ENV`。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
