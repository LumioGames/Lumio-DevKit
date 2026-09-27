# Lumio DevKit

**Lumio 游戏开发 Agent 插件，也是面向开发者的公开使用手册。** 人和 Agent 使用同一份 Markdown；人从本页阅读，Agent 从各个 `SKILL.md` 进入。

## 从你要做的事情开始

| 我要做什么 | 入口 |
| --- | --- |
| 环境、目录、能力导航、升级引擎 | [公共基础](plugin/skills/lumio-development/SKILL.md) |
| 写共享玩法、实体、组件、同步、GAS、Tick | [Gameplay](plugin/skills/lumio-gameplay/SKILL.md) |
| 连接服务器、输入、表现和客户端排障 | [客户端开发](plugin/skills/lumio-client/SKILL.md) |
| 启动服务器、世界、存档和服务端排障 | [服务器开发](plugin/skills/lumio-server/SKILL.md) |
| 制作地图、读写体素和物理查询 | [体素开发](plugin/skills/lumio-voxel/SKILL.md) |
| 编辑表、导出 Reader、双端读取 | [配置表](plugin/skills/lumio-config/SKILL.md) |
| 制作、导出、交接和验收美术资产 | [美术工作流](plugin/skills/lumio-art/SKILL.md) |

## 按顺序学

1. **入门**： [世界模型](plugin/skills/lumio-development/references/capabilities.md) · [环境与第一步](plugin/skills/lumio-development/references/getting-started.md) · [项目布局](plugin/skills/lumio-development/references/project-layout.md) · [升级引擎](plugin/skills/lumio-development/references/getting-started.md#升级引擎)
2. **概念**： [实体与组件](plugin/skills/lumio-gameplay/references/entities-and-components.md) · [同步与 RPC](plugin/skills/lumio-gameplay/references/sync-and-rpc.md) · [GAS 技能](plugin/skills/lumio-gameplay/references/gas-abilities.md) · [Tick](plugin/skills/lumio-gameplay/references/tick.md)
3. **教程**： [Sample 十四步逐步索引](plugin/skills/lumio-development/references/getting-started.md#十四步逐步索引) · [代码生成](plugin/skills/lumio-gameplay/references/code-generation.md) · [体素操作](plugin/skills/lumio-voxel/SKILL.md)
4. **操作**： [Dedicated Server 配置](plugin/skills/lumio-server/references/setup.md) · [本地 Platform 与启动器](plugin/skills/lumio-server/references/development.md) · [日志](plugin/skills/lumio-development/references/diagnostics.md)
5. **参考**： [SDK XML/API](plugin/skills/lumio-development/references/getting-started.md#查公开参考) · [错误码和关闭原因](plugin/skills/lumio-development/references/diagnostics.md#按症状查错误码) · [配表 CLI](plugin/skills/lumio-config/references/edit-and-export.md)
6. **排障**： [分层诊断](plugin/skills/lumio-development/references/diagnostics.md) · [服务器诊断](plugin/skills/lumio-server/references/diagnostics.md) · [客户端诊断](plugin/skills/lumio-client/references/diagnostics.md) · [体素查询](plugin/skills/lumio-voxel/references/queries.md)

这一节只负责导航，操作细节留在对应指引中。

## 安装

本仓同时提供 Agent Plugins 1.0.0 插件包和 Claude Code marketplace。插件本体在 `plugin/`，根目录保留开发、验证和分发入口。

### Agent Plugins 客户端

```sh
npx plugins add LumioGames/Lumio-DevKit
npx plugins add LumioGames/Lumio-DevKit --target codex
```

### Claude Code

```text
/plugin marketplace add LumioGames/Lumio-DevKit
/plugin install lumio-devkit@lumio-devkit
```

### Codex / 手动安装

macOS/Linux 需要 Git 与 Python 3：

```sh
curl -fsSL https://raw.githubusercontent.com/LumioGames/Lumio-DevKit/main/install.sh | bash
```

安装器把完整插件保存到 `$XDG_DATA_HOME/lumio-devkit/plugin`（未设置时为 `~/.local/share/lumio-devkit/plugin`），并把七个 `~/.codex/skills/lumio-*` 指向它。可用 `--target`、`--data-dir` 和 `--dry-run` 调整目标；已有同名目录或外部链接会被拒绝。

### 本地阅读

```sh
git clone https://github.com/LumioGames/Lumio-DevKit.git
cd Lumio-DevKit
bash install.sh --dry-run
```

## 仓库布局

```text
Lumio-DevKit/
  plugin/plugin.json       # 唯一元数据源
  plugin/skills/            # 七个 skill 与 references
  plugin/VERIFICATION.md    # 本轮基线和实际证据
  tools/                    # 生成、校验和安装工具
  tests/                    # 开发验证，不装入插件
```

插件内的相对链接都在 `plugin/` 内可达；开发工具和测试不是使用技能的前置依赖。

## 当前阶段

本轮基线是 **LumioEngineRelease v0.0.2** 与 **LumioSample origin/main `f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb`**，核对日期为 **2026-09-27**。Sample 的十四步入口是 `Tools/launcher.mjs`，公开仓库前置条件为 Git、.NET SDK、Node 和 Docker；每步是否真实通过以 [验证记录](plugin/VERIFICATION.md) 为准。引擎二进制、平台账号和准入票仍需按分发渠道取得，文档不会把静态存在写成双端运行通过。

## 维护

使用方式变化时，更新受影响的指引和验证范围；技术契约仍由引擎维护方提供。版本变化后运行 `python3 tools/sync-manifests.py`，不要手改生成的适配 manifest。

- [贡献与内容维护](CONTRIBUTING.md)
- [验证记录](plugin/VERIFICATION.md)
- [来源与许可证](plugin/NOTICE.md)

本仓原创内容采用 [MIT](LICENSE)。插件不分发引擎二进制。
