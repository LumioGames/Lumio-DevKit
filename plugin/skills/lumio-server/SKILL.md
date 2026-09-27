---
name: lumio-server
description: 使用 Engine 发布物运行 Lumio 游戏服务端，配置 Gameplay、准入、配表与存档，查看 DS 日志并排查启动、连接和恢复失败。不用于修改引擎或服务端基础设施。
---

# Lumio 服务端开发与运行

把游戏的服务端玩法交给 DS（游戏服务器进程），核对配置、连接、玩法结果和存档。

| 任务 | 阅读 |
| --- | --- |
| 准备运行环境、配置和启动 DS | [搭建与配置](references/setup.md) |
| 构建服务端、配表与保存验证 | [开发与验证](references/development.md) |
| 查日志、进不了房或恢复失败 | [日志与排障](references/diagnostics.md) |
| 写实体、同步、技能与每帧系统 | [共享玩法](../lumio-gameplay/SKILL.md) |

先按项目固定的 Engine 版本取得发布物，构建服务端玩法，再运行配置检查和启动器。出现 `DS_READY` 后核对准入和一次目标操作；保存验证应检查同一存储目录上的重启结果。

保留错误码与原日志；普通操作拒绝、服务器故障和存档损坏分别处理。只汇报实际执行的步骤，不用空世界或替身宿主掩盖缺失文件。通用环境见 [Lumio 开发](../lumio-development/SKILL.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
