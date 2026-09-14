# Lumio DevKit

**Lumio 游戏开发 Agent 插件，也是面向开发者的公开使用手册。**

用六个按任务加载的 skill，帮助你组织项目、开发客户端和服务器、使用体素、制作配置表，以及完成美术资产工作流。指引、示例和排障说明只维护一份：人从本页阅读，Agent 从各个 `SKILL.md` 进入。

## 从你要做的事情开始

| 我要做什么 | 入口 |
| --- | --- |
| 第一次使用 Lumio、搭建项目、找能力和开发规范 | [公共基础](plugin/skills/lumio-development/SKILL.md) |
| 连接服务器、输入与表现、同步、客户端日志和调试 | [客户端开发](plugin/skills/lumio-client/SKILL.md) |
| 启动服务器、接入玩法和世界、存档、服务端日志和调试 | [服务器开发](plugin/skills/lumio-server/SKILL.md) |
| 制作方块世界、读写体素、使用加载同步与物理查询 | [体素开发](plugin/skills/lumio-voxel/SKILL.md) |
| 编辑表、校验导出、生成 Reader、双端读取和验证生效 | [配置表](plugin/skills/lumio-config/SKILL.md) |
| 明确美术需求、制作导出资产、交接接入和检查效果 | [美术工作流](plugin/skills/lumio-art/SKILL.md) |

先读 [当前可用范围](plugin/skills/lumio-development/references/capabilities.md)。本插件版本是 **0.2.0**，不代表 SDK 或引擎所有功能的版本、完成度或发布状态。

## 安装

本仓同时提供 **Agent Plugins 1.0.0 插件包**和 **Claude Code marketplace**。插件本体在 `plugin/`；根目录保留开发、验证和分发入口。

### Agent Plugins 客户端

```sh
npx plugins add LumioGames/Lumio-DevKit
```

`plugins` CLI 会发现插件并选择目标宿主。只想安装到 Codex 时可指定：

```sh
npx plugins add LumioGames/Lumio-DevKit --target codex
```

也可以先只检查发现结果：

```sh
npx plugins discover LumioGames/Lumio-DevKit
```

本次核对 `plugins` CLI 1.3.4；它是安装适配器，具体客户端支持取决于该 CLI 与宿主版本，不是 Agent Plugins 标准保证所有宿主采用同一条命令。

### Claude Code

在 Claude Code 中执行：

```text
/plugin marketplace add LumioGames/Lumio-DevKit
/plugin install lumio-devkit@lumio-devkit
```

仓库名是 `Lumio-DevKit`；插件标识和 marketplace 标识都是小写 `lumio-devkit`。安装后重开会话，在技能列表确认六个 `lumio-*` 条目。

### Codex / 手动安装

macOS/Linux，需 Git 与 Python 3：

```sh
curl -fsSL https://raw.githubusercontent.com/LumioGames/Lumio-DevKit/main/install.sh | bash
```

完整插件保存到 `$XDG_DATA_HOME/lumio-devkit/plugin`（未设置时为 `~/.local/share/lumio-devkit/plugin`）；六个 `~/.codex/skills/lumio-*` 是指向它的 symlink。安装器不修改账号、hooks、其他技能或项目规则。默认保留全部参考资料，没有只复制孤立 Markdown 的降级模式。

指定项目级技能目录：

```sh
curl -fsSL https://raw.githubusercontent.com/LumioGames/Lumio-DevKit/main/install.sh | bash -s -- --target .agents/skills
```

可用 `--target ~/.claude/skills` 更换技能目录，`--dry-run` 预览写入位置。已有同名目录或非本安装器的链接时明确拒绝；先检查冲突，不强制覆盖。再次执行会更新完整插件，已有旧版本保留在数据目录的 `releases/` 下。多个 target 共用一份数据目录，更新时一起指向新版；需要独立版本时设置不同的 `--data-dir`。

Windows 优先使用上面的 `npx plugins` 或 Claude marketplace 安装。手动 Python 安装需要可创建目录符号链接的环境。不要同时启用同一份 DevKit 的插件安装和独立技能安装，以免重复发现。

### 本地开发与阅读

```sh
git clone https://github.com/LumioGames/Lumio-DevKit.git
cd Lumio-DevKit
bash install.sh --dry-run
```

直接运行本地 `install.sh` 会使用这份 checkout，便于验证未发布改动。离线已取得仓库时可直接运行 `python3 tools/install.py --target <技能目录>`；不会下载 SDK 或启动游戏服务。

你可以对 Agent 说：

- “用 lumio-development 检查项目的 SDK 和目录。”
- “用 lumio-client 和 lumio-server 定位连接成功后聊天不显示。”
- “用 lumio-config 导出客户端可见表，并验证读取结果。”
- “用 lumio-art 整理方块材质的制作、交接和接入验收。”

也可直接从本页导航阅读同一份内容；没有安装客户端也不影响阅读。

## 仓库布局

```text
Lumio-DevKit/
  .claude-plugin/marketplace.json  # 仓库级 Claude 安装索引
  plugin/                         # 可独立打包的完整插件
    plugin.json                   # Agent Plugins 唯一元数据源
    .claude-plugin/plugin.json    # 自动生成的 Claude 适配
    .codex-plugin/plugin.json     # 自动生成的 Codex 适配
    skills/                       # 六个 skill 和配套 references
    README.md / LICENSE / NOTICE.md / VERIFICATION.md
  install.sh                      # 公共安装入口
  tools/                          # 生成、校验和手动安装工具
  tests/                          # 开发验证，不装入插件
```

插件内链接均在 `plugin/` 内可达；开发工具和测试不会成为使用技能的依赖。

## 当前阶段

内容核对日期：**2026-09-14**。公开示例、配表工具和代码声明可阅读；完整游戏运行还依赖 SDK、匹配的 DS/Bot 分发物和账号服务。核对时 SDK 公共 NuGet 索引为 404，因此这里不承诺裸 clone 后即可完成双端运行。详见 [环境与第一步](plugin/skills/lumio-development/references/getting-started.md)。

各篇分别说明静态核对、局部测试与真实宿主运行的证据边界。未接通的消费者或未取得的分发物不会写成已验证能力。美术 skill 已包含可执行的制作与交接流程；尚未提供的统一导入器不会被当成现有引擎功能。

## 维护

使用方式变化时，更新受影响的指引和示例，并说明核对的版本与验证范围。技术方案、内部实现和契约真源仍由引擎维护；这里解释如何使用公开能力。

- [贡献与内容维护](CONTRIBUTING.md)
- [首版验证记录](plugin/VERIFICATION.md)
- [来源与许可证](plugin/NOTICE.md)

本仓原创内容采用 [MIT](LICENSE)。引用的 SDK、工具、示例与美术资产分别遵守其自己的许可证，本插件不分发引擎二进制。
