# 来源与许可证

Lumio DevKit 的原创指引、技能入口和维护代码采用 MIT，见 `LICENSE`。下列引用内容保留各自许可证；引擎、示例、配表工具和素材的许可证不会因本手册引用而改变。

| 来源 | 用途 | 许可证与归属 |
| --- | --- | --- |
| [Agent Plugins](https://agent-plugins.org/) | 插件 manifest 和目录规范 | 站点文档 CC BY 4.0；规范与 schema 以源仓声明为准；本仓未复制规范正文 |
| [Agent Skills](https://agentskills.io/specification) | `SKILL.md` 格式及按需读取结构 | 以官方站点及仓库许可证为准 |
| [LumioSample](https://github.com/LumioGames/LumioSample) | 游戏示例的代码、资产声明和命令摘录，以及公开源码链接 | 代码与命令 Apache-2.0；Copyright (c) 2026 Lumio (lumio.games)。方块资产目录另用 CC0-1.0 |
| [LumioConfig](https://github.com/LumioGames/LumioConfig) | 配表 CLI、Schema 和 Reader 的公开用法链接 | 见源仓 LICENSE；未复制实现代码 |
| [LumioGame](https://github.com/LumioGames/LumioGame) | 公开项目导航 | Apache-2.0，见源仓 LICENSE |
| [LumioEngineRelease](https://github.com/LumioGames/LumioEngineRelease) | v0.0.2 API、错误码和发布物链接 | 见发布物 LICENSE；未分发引擎实现代码或二进制 |

## LumioSample 摘录

手册的代码与资产声明片段来自 LumioSample 提交 `f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb`，各页在片段旁标注仓根相对路径与许可证。它们是原文件的局部摘录，可能去掉外层缩进；手册的中文说明由 Lumio DevKit 编写。

| Sample 原文件 | 手册用途 |
| --- | --- |
| `Gameplay/EntityTypes/BoxEntity.cs` | 箱子实体与组件声明 |
| `Gameplay/Components/Chat/ChatComponent.cs` | 同步字段与远程调用声明 |
| `Gameplay/Abilities/MineAbility.cs` | 挖矿技能与预测策略 |
| `Gameplay/Abilities/MineAbility.Client.cs` | 客户端查询与地形预测 |
| `Gameplay/Abilities/MoveAbility.cs` | 移动碰撞查询 |
| `Gameplay/SampleMiningComponent.Server.cs` | 服务器提交地形修改 |
| `Gameplay/SampleMiningSystem.Server.cs` | 每帧系统入口 |
| `Gameplay/Config/SampleConfigBinding.cs` | 配置装载与世界绑定 |
| `Client/Bots/SampleMiningScenario.cs` | Bot 操作与玩法验证 |
| `Client/Assets/Blocks/lumio.stone.json` | 方块资产声明，CC0-1.0 |
| `README.md`、`.github/workflows/tour.yml`、`Gameplay/Tables/README.md`、`Client/UI/Spectator/README.md` | 安装、构建、导览、配表和浏览器命令，Apache-2.0 |
| `Client/Assets/Blocks/README.md` | 方块素材生成与检查命令，CC0-1.0 |

Apache-2.0 全文见 [随包许可证](licenses/LumioSample-Apache-2.0.txt) 与 [上游 LICENSE](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/LICENSE)。

`Client/Assets/Blocks/lumio.stone.json` 由 LumioSample contributors 创建，按该目录的 [LICENSE](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Client/Assets/Blocks/LICENSE) 使用 [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/legalcode)，不属于仓根 Apache-2.0 的代码摘录。该目录的 README 命令同样使用 CC0-1.0；随包保留 [上游素材许可说明](licenses/LumioSample-Blocks-CC0.txt)。手册没有复制此目录的纹理图片。

美术作品、字体和外部素材的授权需要逐项保留；引用示例目录不授予其中外部素材的额外使用权。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
