---
name: lumio-gameplay
description: 在 Gameplay/ 编写两端共享的实体、组件、同步与 GAS 玩法；需要按端拆文件、理解 Tick 或检查生成注册表时使用。
license: MIT
---

# Lumio 玩法开发

这个技能说明怎样在 `Gameplay/` 写游戏规则：实体和组件描述状态，GAS 处理技能和效果，生成器把声明接到运行时注册表。先按任务读取一篇参考，不要把引擎内部实现复制到游戏仓。

## 按任务读取

| 任务 | 参考 |
| --- | --- |
| 设计实体、组件或方块实体 | [实体与组件](references/entities-and-components.md) |
| 决定字段可见范围、拆分双端代码或加 RPC | [同步与 RPC](references/sync-and-rpc.md) |
| 写技能、效果、属性、预测或回滚 | [GAS 技能](references/gas-abilities.md) |
| 判断一帧内的执行顺序，编写系统 | [Tick 顺序](references/tick.md) |
| 修改声明后更新注册表 | [代码生成](references/code-generation.md) |

## 先核对什么

1. 确认当前游戏的 `Gameplay/` 布局和 SDK 版本；通用目录约定见 [项目布局](../lumio-development/references/project-layout.md)。
2. 共享声明放在没有端后缀的文件，服务器和客户端的实现分别放在 `.Server.cs` 与 `.Client.cs`；不要手改 `generated/`。
3. 技能、冷却、消耗与预测都走 GAS。体素格子只保存方块，库存、储量和生命周期放在实体组件；需要固定位置又有逻辑时使用方块实体。
4. 编译生成结果后再做真实 Host 验证。文件存在或生成注册表出现，不等于网络、预测或冷恢复已经跑通。

服务端和客户端的宿主接入分别见 [lumio-server](../lumio-server/SKILL.md) 与 [lumio-client](../lumio-client/SKILL.md)；体素读写和缺块处理见 [lumio-voxel](../lumio-voxel/SKILL.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
