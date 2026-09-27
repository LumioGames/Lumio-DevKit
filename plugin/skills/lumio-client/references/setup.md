# 搭建与运行客户端

Sample 用 Bot（自动操作的客户端）走完游戏流程，也提供浏览器旁观页面。

## 跑完十四步

前置条件是 Git、[global.json](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/global.json) 要求的 .NET SDK、Node.js 22 和 Docker。引擎通过 `Engine/` 子模块取得；本机平台须是发布物提供的 `win-x64` 或 `linux-x64`。首次获取见 [开始开发](../../lumio-development/references/getting-started.md)。

在 Sample 根目录执行 [README](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/README.md) 中的命令（Apache-2.0）：

```sh
dotnet build LumioSample.slnx
dotnet build Gameplay/Lumio.Sample.Gameplay.csproj -p:LumioEcsSide=client
dotnet build Client/Bots/Lumio.Sample.Bots.csproj
node Tools/launcher.mjs --bots 2 --stagger-ms 250 --scenario-dll Client/Bots/bin/Debug/net10.0/Lumio.Sample.Bots.dll
```

`LumioEcsSide=client` 选择客户端代码与注册表，排除 `*.Server.cs`。服务端输出在 `net10.0`，客户端输出在 `net10.0-client`，避免互相覆盖。

启动器负责 Platform（账号和房间服务）、DS（游戏服务器）、各账号的房间票和 Bot。第一个 Bot 使用 `SampleMiningScenario` 挖矿和拾取；第十四步重启 DS，由 `SampleRestoreVerifyScenario` 验证恢复。检查十四步结果和最终 `VERIFICATION_STATUS`，日志位置见 `EVIDENCE_PATH`。

[Clean-machine tour 工作流](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/.github/workflows/tour.yml) 配置为每天及 main 推送时，在全新 Ubuntu runner 上匿名递归克隆、构建、测试并调用上述命令。这是有明确前置条件的一键导览；某次运行是否成功，查看对应工作流结果与日志。完整 `dotnet test` 还需要 Python 3.11+ 和相邻的公开 LumioConfig 检出，见 [Sample README](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/README.md)。

## 浏览器旁观页面

spectator（旁观客户端）需要 .NET 的 `wasm-tools` 工作负载和支持 WebGL2 的浏览器。浏览器工程不在 `LumioSample.slnx` 中，须单独构建发布；构建命令摘自 Apache-2.0 的 [Client/UI/Spectator/README.md](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Client/UI/Spectator/README.md)：

```sh
dotnet build Gameplay/Lumio.Sample.Gameplay.csproj -c Release -p:LumioEcsSide=client -p:LumioBrowserReplica=true
dotnet publish Client/UI/Spectator/host/Lumio.Sample.Client.Spectator.csproj -c Release -p:LumioEcsSide=client -p:LumioBrowserReplica=true
node Tools/launcher.mjs --bots 2 --stagger-ms 250 --scenario-dll Client/Bots/bin/Debug/net10.0/Lumio.Sample.Bots.dll --spectator
```

先完成上面的普通客户端与 Bot 构建，再执行浏览器步骤。启动命令沿用十四步的场景 DLL，并增加启动器提供的 `--spectator` 参数；单独传这个参数不能替代场景配置。浏览器玩法用 `netstandard2.1` 编译，放入 `net10.0-browser` 输出目录。启动器通过 HTTP 提供 `Client/UI/Spectator/host/bin/Release/net10.0/publish/wwwroot`，为页面注入单独旁观票；打开控制台打印的地址。

默认页面是俯视图，在地址后加 `?view=blocks` 才是 WebGL2 三维方块视图。材质接入见 [美术验收](../../lumio-art/references/integration-and-review.md)。

## 失败时查哪里

缺 Engine 文件先初始化子模块；缺工作负载按 .NET 提示安装；白屏时查 `_framework/`、WASM 和页面资源请求。完整页面在发布目录，不能用源码目录或 `file:` 打开代替。连接、准入和业务结果的区分见 [客户端排障](diagnostics.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
