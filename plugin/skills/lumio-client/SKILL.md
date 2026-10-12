---
name: lumio-client
description: 构建 Lumio 客户端玩法和 Bot 场景，运行 Sample 十四步与浏览器旁观页面，排查连接、准入、输入和客户端显示。不用于修改引擎客户端基础设施。
---

# Lumio 客户端开发

把玩家操作交给现有宿主，接收服务器结果并显示画面。

| 任务 | 阅读 |
| --- | --- |
| 构建客户端、跑十四步或浏览器页面 | [搭建与运行](references/setup.md) |
| 写 Bot、提交输入、接入表现 | [客户端开发](references/development.md) |
| 查准入、操作失败、掉线或白屏 | [日志与排障](references/diagnostics.md) |
| 共享实体、同步与 GAS 技能 | [共享玩法](../lumio-gameplay/SKILL.md) |

先核对 Engine 发布物和客户端侧构建，再运行一个目标场景。分别确认进程启动、连接准入、请求被接受与服务器实际应用；接收方世界或画面是业务结果的检查点。

预测、冷却和技能统一走 GAS（挂在实体上的技能系统），只供画面使用的东西可以是本地实体。保留拒绝原因，不直接重发结果未知的输入。环境准备见 [Lumio 开发](../lumio-development/SKILL.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
