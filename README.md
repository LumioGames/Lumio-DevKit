# Lumio DevKit

**Lumio 游戏开发 Agent 插件，也是面向开发者的公开使用手册。**

用六个按任务加载的 skill，帮助你组织项目、开发客户端和服务器、使用体素、制作配置表，以及完成美术资产工作流。指引、示例和排障说明只维护一份：人从本页阅读，Agent 从各个 `SKILL.md` 进入。

## 从你要做的事情开始

| 我要做什么 | 入口 |
| --- | --- |
| 第一次使用 Lumio、搭建项目、找能力和开发规范 | [公共基础](skills/lumio-development/SKILL.md) |
| 连接服务器、输入与表现、同步、客户端日志和调试 | [客户端开发](skills/lumio-client/SKILL.md) |
| 启动服务器、接入玩法和世界、存档、服务端日志和调试 | [服务器开发](skills/lumio-server/SKILL.md) |
| 制作方块世界、读写体素、使用加载同步与物理查询 | [体素开发](skills/lumio-voxel/SKILL.md) |
| 编辑表、校验导出、生成 Reader、双端读取和验证生效 | [配置表](skills/lumio-config/SKILL.md) |
| 明确美术需求、制作导出资产、交接接入和检查效果 | [美术工作流](skills/lumio-art/SKILL.md) |

先读 [当前可用范围](skills/lumio-development/references/capabilities.md)。本插件版本是 **0.1.0**，不代表 SDK 或引擎所有功能的版本、完成度或发布状态。

## 安装和阅读

```sh
git clone https://github.com/LumioGames/lumio-devkit.git
```

在支持 [Agent Plugins 1.0.0](https://agent-plugins.org/) 的宿主中，按该宿主的插件安装方式选择本目录或仓库。标准定义根 `plugin.json` 和 `skills/` 布局；具体安装、启用、更新命令由宿主决定，本项目不提供一条假定所有宿主都支持的安装命令。

在技能列表中确认六个 `lumio-*` 条目。可以这样提出任务：

- “用 lumio-development 指引帮我检查新项目的 SDK 和目录。”
- “用 lumio-client 和 lumio-server 定位连接成功后聊天不显示的问题。”
- “用 lumio-config 导出客户端可见的表，并验证读取结果。”
- “用 lumio-art 为一套方块材质整理制作、交接和接入验收步骤。”

宿主没有插件功能时，仍可直接阅读本手册；若宿主支持独立 Agent Skills，可按其文档加载所需技能。复制或链接时保留本插件内跨技能引用需要的完整目录。仅执行 clone 不意味着宿主已加载技能。

## 当前阶段

内容核对日期：**2026-09-14**。公开示例、配表工具和代码声明可阅读；完整游戏运行还依赖 SDK、匹配的 DS/Bot 分发物和账号服务。核对时 SDK 公共 NuGet 索引为 404，因此这里不承诺裸 clone 后即可完成双端运行。详见 [环境与第一步](skills/lumio-development/references/getting-started.md)。

各篇分别说明静态核对、局部测试与真实宿主运行的证据边界。未接通的消费者或未取得的分发物不会写成已验证能力。美术 skill 已包含可执行的制作与交接流程；尚未提供的统一导入器不会被当成现有引擎功能。

## 维护

使用方式变化时，更新受影响的指引和示例，并说明核对的版本与验证范围。技术方案、内部实现和契约真源仍由引擎维护；这里解释如何使用公开能力。

- [贡献与内容维护](CONTRIBUTING.md)
- [首版验证记录](VERIFICATION.md)
- [来源与许可证](NOTICE.md)

本仓原创内容采用 [MIT](LICENSE)。引用的 SDK、工具、示例与美术资产分别遵守其自己的许可证，本插件不分发引擎二进制。
