# 搭建与运行客户端

本页针对 Engine v0.0.2 的客户端/Bot 发布物。公开 Sample 的十四步前置是 Git、.NET SDK、Node 和 Docker；仍需同一发布的 `Lumio.Client.Bot.Host.dll`、Native 库、sidecar、游戏客户端程序集和 Platform launch 票。

## 编译客户端侧 Gameplay

```sh
git clone --recursive https://github.com/LumioGames/LumioSample.git my-game
cd my-game
dotnet build Gameplay/Lumio.Sample.Gameplay.csproj -p:LumioEcsSide=client
```

`LumioEcsSide=client` 让 SDK 选择客户端生成注册表并排除 `*.Server.cs`；默认构建是服务器侧。输出目录与 DS 使用的服务器输出分开，避免用客户端 DLL 覆盖服务器程序集。Engine SDK 只从 `Engine/` 子模块解析，不能再传旧的 `-p:LumioLocalFeed=`。

## 运行 Bot

前置：DS 已打印 `DS_READY`，Platform 为当前账号和房间签发 launch 票，`BOT_HOST_DLL`、`GAMEPLAY_CLIENT_DLL`、`ENGINE_NATIVE` 来自同一 Engine v0.0.2 发布。通过环境变量或受限 manifest 注入票，不要放在 URL、命令历史或仓库：

```sh
dotnet "$BOT_HOST_DLL" \
  --server "$DS_ENDPOINT" \
  --gameplay "$GAMEPLAY_CLIENT_DLL" \
  --engine-native "$ENGINE_NATIVE" \
  --account-from Bot01 --account-to Bot01 \
  --log-dir .run/bot01 --log-min-level debug
```

观察 `admission-events.ndjson` 的 `admitted`，再与 DS 日志中的账号和连接代次对齐。每个账号必须使用自己的 launch 票。

## Sample 十四步

完整导览由 `Tools/launcher.mjs` 驱动，Bot 场景程序集来自 `Client/Bots/Lumio.Sample.Bots.csproj`。在已满足 Docker、Platform 和 Engine 前置时运行：

```sh
dotnet build Client/Bots/Lumio.Sample.Bots.csproj
node Tools/launcher.mjs --bots 2 \
  --scenario-dll Client/Bots/bin/Debug/net10.0/Lumio.Sample.Bots.dll
```

Bot 1 执行挖矿导览，步骤 05–13 根据 DS 日志和 `result.ndjson` 判定；第 14 步在同一 store 上重启 DS 并由 `SampleRestoreVerifyScenario` 核对恢复。缺少 Platform、Bot.Host、Engine 或票时只报告 `BLOCKED_ENV`，不自动切换成假客户端。

## 浏览器 spectator

Sample 的 WebGL2/浏览器路线使用已发布的 spectator bundle。先按 `Client/UI/Spectator/README.md` 构建并发布，再由 `Tools/launcher.mjs --spectator` 通过 HTTP(S) 提供 `wwwroot`。直接打开 `file:`、只有空 HTML 或没有 `_framework/` 不能算客户端接通。浏览器 close code 与错误原因见 [按症状查错误码](../../lumio-development/references/diagnostics.md#按症状查错误码)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
