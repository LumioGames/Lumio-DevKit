---
name: lumio-voxel
description: 使用 Lumio 已发布的体素 API 制作地图、地形查询与挖掘玩法，处理未知区域、修订冲突及方块实体。不用于实现 Native 内核、网格算法或存储格式。
---

# Lumio 体素玩法

体素（方块地形）负责静态占格；实体保存玩家、掉落和箱子等对象的逻辑。

| 任务 | 阅读 |
| --- | --- |
| 地图、方块与箱子怎样配合 | [世界与地图](references/world-and-maps.md) |
| 读格子、移动扫掠和未知区域 | [查询](references/queries.md) |
| 挖穿、地形提交和失败结果 | [写入](references/mutations.md) |
| 实体、技能与每帧执行顺序 | [共享玩法](../lumio-gameplay/SKILL.md) |
| 方块资源与 WebGL2 显示 | [世界资产](../lumio-art/references/world-assets.md) |

先用 Sample 已有的适配器读格子和修订，再做玩法判断，最后排入写入。请求被接受后还要检查实际应用结果，未知数据不能当空气。

`BlockId` 使用 `uint`。技能、冷却与预测通过 GAS（挂在实体上的技能系统）管理；服务器和客户端读取各自世界。环境前置见 [开始开发](../lumio-development/references/getting-started.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
