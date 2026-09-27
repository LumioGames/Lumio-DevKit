# 环境与第一步

这一页说明怎样拿到与 **Engine v0.0.2** 匹配的示例、验证工具链，再开始写玩法。

## 1. 准备工具和发布物

公开 Sample 的完整导览需要 Git、.NET SDK（按 `global.json` 安装）、Node.js 22 和可运行的 Docker。Engine v0.0.2 提供 Windows x64、Linux x64 发布物。先检查工具版本：

```sh
git --version
dotnet --version
node --version
docker --version
```

Sample 的默认 C# 工程使用 .NET 10；浏览器工程另有目标框架。Docker 需要已经启动，启动器会用发布物自带的 Compose 配置启动本地 Platform（账号、房间和准入服务），并为本地导览准备测试账号。运行配表测试还需 Python 3.11 以上和同级的公开 LumioConfig 检出。

## 2. 取得示例和 Engine

从公开仓库递归 clone，Engine 子模块会固定到游戏提交声明的发布物：

```sh
git clone --recursive https://github.com/LumioGames/LumioSample
cd LumioSample
git rev-parse HEAD
git submodule status Engine
```

如果已经 clone 但 `Engine/` 为空：

```sh
git submodule update --init --depth 1 Engine
```

当前 Sample 通过 `Directory.Build.props` 读取 `Engine/manifest.json` 的版本；`NuGet.config` 把引擎包限定到 `Engine/sdk/`，`Directory.Build.targets` 在发布物缺失时报告 `LUMIO_SDK_UNRESOLVED`。无需额外的本地引擎包源。

## 从模板建游戏

先在 [LumioSample](https://github.com/LumioGames/LumioSample) 页面选择 **Use this template → Create a new repository**，填写自己的仓库名，再 clone 新仓库并带上 `--recursive`。如果模板创建后的检出没有初始化子模块，在新仓根执行前面的 `git submodule update --init --depth 1 Engine`。保留模板的目录与生成流程，从修改一个玩法或一张表开始；共享代码的组织见 [项目布局](project-layout.md)。

## 升级引擎

升级引擎只使用 Sample 提供的脚本。脚本会检查发布物再切换子模块指针：

```sh
node Tools/update-engine.mjs <版本>
# 例如：
node Tools/update-engine.mjs 0.0.2
```

## 跑示例十四步导览

先验证游戏侧编译和生成文件：

```sh
dotnet build LumioSample.slnx
```

共享玩法位于 `Gameplay/`。同一个 `Gameplay/Lumio.Sample.Gameplay.csproj` 按构建参数产出服务器或客户端代码；Bot 工程是 `Client/Bots/Lumio.Sample.Bots.csproj`。

`Tools/launcher.mjs` 是完整导览入口：它启动 Platform、DS（运行房间的专用服务器）和 C# Bot（模拟玩家的客户端），输出十四个 `step=NN` 结果，第十四步重启同一存档验证恢复。先编译客户端玩法和 Bot，再运行启动器；以下命令与 Sample `README.md` 和 `.github/workflows/tour.yml` 一致：

```sh
dotnet build Gameplay/Lumio.Sample.Gameplay.csproj -p:LumioEcsSide=client
dotnet build Client/Bots/Lumio.Sample.Bots.csproj
node Tools/launcher.mjs --bots 2 --stagger-ms 250 --scenario-dll Client/Bots/bin/Debug/net10.0/Lumio.Sample.Bots.dll
```

`.github/workflows/tour.yml` 在推送 main 和每日计划中执行上述导览。启动器遇到缺 Docker、发布物不含本机平台等情况会报告 `BLOCKED_ENV` 并退出；先补齐报告的前置条件。每个 Bot 单独取得 launch 票（允许进入指定房间的临时凭证）；记录日志时去掉票与密码。

### 十四步逐步索引

下面的名称和顺序来自 [`Tools/tour-steps.mjs`](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Tools/tour-steps.mjs)。每一步的原始证据保存在 `.run/` 下的 DS 日志、Bot `result.ndjson` 和启动器摘要中；启动器被强制清理的进程不算通过。

| 步骤 | Sample 名称 | 阅读入口 |
| --- | --- | --- |
| 01 | 编译配表 (`compile-config`) | [配置导出](../../lumio-config/references/edit-and-export.md) |
| 02 | 注册登录 (`account-login`) | [服务器配置](../../lumio-server/references/setup.md) |
| 03 | 起 DS (`start-ds`) | [服务端开发](../../lumio-server/references/development.md) |
| 04 | 进房间 (`admit-room`) | [客户端搭建](../../lumio-client/references/setup.md) |
| 05 | 加载底图 (`load-basemap`) | [世界与地图](../../lumio-voxel/references/world-and-maps.md) |
| 06 | 玩家入场 (`spawn-player`) | [实体与组件](../../lumio-gameplay/references/entities-and-components.md) |
| 07 | 跑动 (`move`) | [体素查询](../../lumio-voxel/references/queries.md) |
| 08 | 聊天 (`chat`) | [同步与 RPC](../../lumio-gameplay/references/sync-and-rpc.md) |
| 09 | 挖掘 (`mine`) | [GAS 技能](../../lumio-gameplay/references/gas-abilities.md) |
| 10 | 矿脉储量 -1 (`vein-reserve`) | [GAS 技能](../../lumio-gameplay/references/gas-abilities.md) |
| 11 | 方块变空气 (`cell-to-air`) | [体素写入](../../lumio-voxel/references/mutations.md) |
| 12 | 掉出矿石 (`ore-drop`) | [GAS 技能](../../lumio-gameplay/references/gas-abilities.md) |
| 13 | 拾取 (`pickup`) | [GAS 技能](../../lumio-gameplay/references/gas-abilities.md) |
| 14 | 存档重启 (`save-restore`) | [保存与重启验证](../../lumio-server/references/development.md#保存与重启验证) |

## 查公开参考

下载 [Engine v0.0.2 SDK 包](https://github.com/LumioGames/LumioEngineRelease/raw/refs/tags/v0.0.2/sdk/Lumio.Engine.SDK.0.0.2.nupkg)，或打开本地 `Engine/sdk/Lumio.Engine.SDK.0.0.2.nupkg`。这是 ZIP 格式，可用解压工具打开；不要在 `Engine/` 中修改发布物。包内有：

- `content/docs/public-api.md`：公开 API（供游戏调用的接口）索引。
- `lib/net10.0/*.xml`：程序集参考，如 `Lumio.Engine.SDK.xml`、`Lumio.GameRuntime.Ecs.xml`、`Lumio.GameRuntime.Gas.xml`。
- `content/docs/error-codes.md`：完整错误码表。
- `content/wire/ds-transport-v1.json` 的 `closeCodes`：WebSocket 关闭原因、数值和客户端动作的完整表。

常见问题先查 [按症状查错误码](diagnostics.md#按症状查错误码)。

## 从一个小改动开始

推荐先阅读 `Gameplay/Components/Chat/ChatComponent.cs` 与对应的 `.Server.cs`/`.Client.cs`，只改变一处服务端日志或 UI 文案，再重新构建。验证聊天时使用两个独立连接，在服务器和接收方日志中对齐同一条消息。

操作命令和目录依据 [Sample README](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/README.md) 与 [导览工作流](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/.github/workflows/tour.yml)，许可证 Apache-2.0。本次命令结果见 [验证记录](../../../VERIFICATION.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
