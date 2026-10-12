---
name: lumio-gameplay
description: 在 Gameplay/ 编写两端共享的实体、组件、同步与 GAS 玩法；需要按端拆文件、理解 Tick 或检查生成注册表时使用。
license: MIT
---

# Lumio 玩法开发

在 `Gameplay/` 写游戏规则：实体和组件描述状态，GAS（玩法技能系统）处理技能、冷却和预测，生成器把声明接到运行时注册表。按任务读取一篇参考。

## 按任务读取

| 任务 | 参考 |
| --- | --- |
| 设计实体、组件或方块实体 | [实体与组件](references/entities-and-components.md) |
| 决定字段可见范围、拆分双端代码或加 RPC | [同步与 RPC](references/sync-and-rpc.md) |
| 写技能、效果、属性、预测或回滚 | [GAS 技能](references/gas-abilities.md) |
| 判断一帧内的执行顺序，编写系统 | [Tick 顺序](references/tick.md) |
| 修改声明后更新注册表 | [代码生成](references/code-generation.md) |

## 先核对什么

1. 确认游戏目录与引擎版本，见 [项目布局](../lumio-development/references/project-layout.md)。
2. 示例只摘自本页基线上的 Sample，保留相对路径和提交号；示例中尚未提供的能力不要编造。
3. 共享声明与 `.Server.cs` / `.Client.cs` 按端编译；改声明后重新构建，不手改 `generated/`。

宿主接入见 [lumio-server](../lumio-server/SKILL.md) 与 [lumio-client](../lumio-client/SKILL.md)；体素读写和缺块处理见 [lumio-voxel](../lumio-voxel/SKILL.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）