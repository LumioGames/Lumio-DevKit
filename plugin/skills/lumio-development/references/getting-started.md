# 环境与第一步

这一页说明怎样拿到与 **Engine v0.0.2** 匹配的示例、验证工具链，再开始写玩法。

## 1. 准备工具和发布物

公开 Sample 的学习路径需要 Git、.NET SDK、Node 和 Docker。先在目标机器检查版本：

```sh
git --version
dotnet --version
node --version
docker --version
```

Sample 的 C# 工程目标是 .NET 10；Node 脚本由仓库自己的 `package.json`/脚本约束版本。命令可调用只证明工具存在，不证明账号、平台、DS 或客户端发布物可用。真实双端还需要与游戏程序集同一版本的 Engine Release、Bot/客户端宿主、平台 launch 配置和测试账号。

## 2. 取得示例和 Engine

从公开仓库递归 clone，Engine 子模块会固定到游戏提交声明的发布物：

```sh
git clone --recursive https://github.com/LumioGames/LumioSample.git my-game
cd my-game
git rev-parse HEAD
git submodule status Engine
```

如果已经 clone 但 `Engine/` 为空：

```sh
git submodule update --init --depth 1 Engine
```

不要再使用 `-p:LumioLocalFeed=` 指向旧的本地 NuGet feed。当前 Sample 的 `Directory.Build.targets` 只从 `Engine/` 子模块读取 `manifest.json` 和 `sdk/` 下的 `Lumio.Engine.SDK.<version>.nupkg`；缺失时会明确报 `LUMIO_SDK_UNRESOLVED`。

### 升级引擎

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

共享玩法位于 `Gameplay/`；服务端、客户端和 Bot 的实际工程分别在 `Gameplay/Lumio.Sample.Gameplay.csproj`、`Client/Bots/Lumio.Sample.Bots.csproj`。不要把输出目录里的旧 DLL 当作本次构建证据。

完整导览的唯一入口是 `Tools/launcher.mjs`，它启动 Platform、DS 和 C# Bot，输出十四个 `step=NN` 结果，并在第十四步重启同一存档验证恢复。准备好 Docker、Engine 发布物、平台配置和场景程序集后运行：

```sh
node Tools/launcher.mjs --bots 2 \
  --scenario-dll Client/Bots/bin/Debug/net10.0/Lumio.Sample.Bots.dll
```

`Tools/launcher.mjs` 缺少 Engine、Platform、Bot.Host、准入票或场景 DLL 时会明确标记 `BLOCKED_ENV`；这属于缺运行环境，不应改成“通过”。每个 Bot 使用自己的 launch 票；不要把普通账号凭据放进 URL、仓库或日志。

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

Engine v0.0.2 随包提供程序集 XML（例如 `Lumio.Engine.SDK.xml`、`Lumio.GameRuntime.Ecs.xml`、`Lumio.GameRuntime.Gas.xml`）和公开 wire/契约文件。以实际发布物中的 XML、README 和 Sample `Tools/` 为准核对精确签名；不要从私有引擎仓或旧文章猜 API。常见体素码见 [按症状查错误码](diagnostics.md#按症状查错误码)，完整表见 [SDK 包目录](https://github.com/LumioGames/LumioEngineRelease/tree/v0.0.2/sdk) 中的 `content/docs/error-codes.md`。

## 5. 从一个小改动开始

推荐先阅读 `Gameplay/Components/Chat/ChatComponent.cs` 与对应的 `.Server.cs`/`.Client.cs`，只改变一处服务端日志或 UI 文案，再重新构建。构建通过只证明编译；要证明聊天送达，需要两个独立连接并在服务器和接收方日志中对齐同一条消息。

## 证据边界

- **能力不存在**：发布物没有所需类型或命令，记录为上游缺口。
- **尚未接线**：代码声明存在，但宿主没有提供对应运行输入。
- **缺运行环境**：缺 Docker、Platform、Engine 或票，导览停在具体步骤并标 `BLOCKED_ENV`。
- **本次未验证**：没有实际执行的命令，不写成通过。

公开核对基线、命令结果和 Sample 路径表见 [验证记录](../../../VERIFICATION.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
