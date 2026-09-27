---
name: lumio-development
description: Lumio 游戏项目上手、SDK 环境检查、能力导航、目录与命名规范，以及跨客户端和服务器的问题初步定位。需要使用引擎做游戏或判断任务归属时使用；引擎内部架构与算法实现不在本技能范围内。
license: MIT
---

# Lumio 开发基础

帮助开发者在现有 Lumio 项目中完成任务，或从公开模板开始。先确认正在使用的项目、SDK/宿主版本与目标平台，不替换用户选定的产品和技术路线。

## 按任务读取

| 任务 | 阅读 |
| --- | --- |
| 首次使用、SDK 找不到、准备公开模板 | [环境与第一步](references/getting-started.md) |
| 新文件放哪里、双端代码如何拆、如何生成声明 | [项目布局与规范](references/project-layout.md) |
| 写实体、组件、同步、GAS、Tick | [共享 Gameplay](../lumio-gameplay/SKILL.md) |
| 想知道能力是否存在、入口和限制 | [能力与证据范围](references/capabilities.md) |
| 连接、加载、同步或执行结果异常 | [日志与分层定位](references/diagnostics.md) |

不为普通任务遍历整本手册。先选当前问题所属的参考，再读源码或对应领域技能。

## 工作方式

1. 从项目已有入口与依赖声明确认运行方式；已有项目沿用其布局，新项目参考模板。
2. 先查已有能力和公开 API，再决定是否需要新增玩法代码。缺 SDK 分发物时说明缺什么，不生成替身使构建“成功”。
3. 技能、冷却、消耗与预测使用 GAS；实体与体素按 [能力说明](references/capabilities.md) 分工。操作拒绝不自动等于整个世界故障。
4. 使用 SDK 随附的 XML、公开 API/错误码参考和机器契约查精确签名，不从手册的说明性示例推导未提供的 API。
5. 交回实际修改、运行命令与结果、未验证范围；使用说明变化时更新受影响的一处文档。

## 进入领域

- [客户端](../lumio-client/SKILL.md)：输入、连接、同步、表现及调试。
- [服务器](../lumio-server/SKILL.md)：宿主、世界、玩法、存档及调试。
- [共享 Gameplay](../lumio-gameplay/SKILL.md)：实体、组件、同步、技能、Tick 和代码生成。
- [体素](../lumio-voxel/SKILL.md)：地图、读写与物理查询。
- [配置表](../lumio-config/SKILL.md)：表源到双端 Reader。
- [美术](../lumio-art/SKILL.md)：需求、制作、交接与接入验收。

这些指引提供开发方法，不代表已获准推送代码、发布服务或操作生产数据；执行范围以当前用户任务为准。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
