# 搭建与运行客户端

适用范围：使用已取得的 SDK 与客户端宿主产物。核对日期为 2026-09-14；通用包取得、版本与工具链见 [开始开发](../../lumio-development/references/getting-started.md)。当前不能假设干净机器从 nuget.org 就能取得所需包。

## 准备实际产物

除游戏项目外，需要同一发布的 `Lumio.Client.Bot.Host.dll`、其 `.deps.json` / `.runtimeconfig.json` 和依赖程序集；真实连接还需要匹配平台架构的 Native 动态库及其身份 sidecar。仅有 `Lumio.Engine.SDK` 并不证明这些 Host 产物也已交付。缺少产物时向分发方取得完整客户端包，不添加私有源码路径作为公开搭建步骤。

公开阅读样本：[LumioSample 固定版本](https://github.com/LumioGames/LumioSample/tree/b236d2e12206dd1f5b12a9958810d92c2f49f13c)。示例使用 .NET 10；在按通用指南准备好本地 SDK feed 后，从示例根目录编译客户端：

```sh
dotnet build src/Lumio.Sample.Gameplay/Lumio.Sample.Gameplay.csproj \
  -c Release -p:LumioEcsSide=client \
  -p:LumioLocalFeed="$LUMIO_SDK_FEED" -o .run/client
```

`LUMIO_SDK_FEED` 是本例约定的本地 feed 路径变量，不是 SDK 自动识别的配置键；实际传入的是 `LumioLocalFeed`。预期输出 `.run/client/Lumio.Sample.Gameplay.dll` 及依赖。`LumioEcsSide=client` 选择客户端生成声明并排除 `*.Server.cs`；默认构建是服务器侧。服务器输出放另一个目录，避免同名 DLL 被覆盖。生成文件的边界见 [项目布局](../../lumio-development/references/project-layout.md)。

## 先跑一个真实 Bot

前置条件：DS 已报告 `DS_READY`；平台已为当前账号、房间和版本签发 launch 准入票；下例中的 `BOT_HOST_DLL`、`GAMEPLAY_CLIENT_DLL`、`ENGINE_NATIVE` 是本地完整路径，`DS_ENDPOINT` 来自真实就绪记录。

通过安全的进程环境注入 `LumioBotAdmissionTicket`。不要把票写入 URL、版本库或示例命令文本。常驻 Bot 的启动形式为：

```sh
dotnet "$BOT_HOST_DLL" \
  --server "$DS_ENDPOINT" \
  --gameplay "$GAMEPLAY_CLIENT_DLL" \
  --engine-native "$ENGINE_NATIVE" \
  --account-from Bot01 --account-to Bot01 \
  --log-dir .run/bot01 --log-min-level debug
```

账号名必须与准入票对应；`Bot*` 账号还需要平台分配的 Bot 工具凭据。这条命令启动常驻客户端，不会因为收到 Welcome 就退出。观察 `admission-events.ndjson` 中 `admitted`，并在 DS 日志中对齐账号和连接代次。后续验证具体 RPC 或玩法结果见 [开发接缝](development.md)。

扩大到多账号前，先取得每个账号独立的票。常驻入口支持 `--admission-ticket` 指向账号 manifest；结构是 `accounts[]`，每项含 `loginName` 与 `launch.admissionCredential`，文件应保存在受限、忽略提交的位置。带 `--scenario` 的入口不按这个 manifest 枚举账号；当前 `--bots N` 会复用同一张票，不能把它当成 N 个独立玩家的真实压测。

## 使用 C# 场景

先按 [开发接缝](development.md) 编译场景 DLL，确保它引用分发方提供的兼容 Bot API。对真实 DS 使用单 Bot：

```sh
dotnet "$BOT_HOST_DLL" \
  --gameplay "$GAMEPLAY_CLIENT_DLL" \
  --scenario "$SCENARIO_DLL" --scenario-name Guide.ChatOnce \
  --server "$DS_ENDPOINT" --engine-native "$ENGINE_NATIVE" \
  --account-from Bot01 --bots 1 --ticks 120 --seed 17 \
  --log-dir .run/chat-once
```

这里同样从 `LumioBotAdmissionTicket` 取房间票。预期 `result.ndjson` 写出词表、步骤、命令接收结果、上行统计与断言；`--ticks` 是场景宿主循环预算，不是“运行多少秒”。

只有需要明确的本地协议 fixture 时，才去掉真实连接参数并同时传入：

```text
--transport local-embedded --fixture foundation-happy-path
```

该 fixture 只证明这一组固定会话/输入路径。它不证明 Native、平台验票、体素碰撞、存档或真实 DS 已成功。普通场景缺服务器、票或 Native 时会 `BLOCKED`（退出 8），不会自动换成 fixture；装载失败可能更早返回 20–25。

## 浏览器与 Hello 的边界

当前可见浏览器路线是 .NET WASM 的 spectator，由 C# 消费副本结果，JS 绘制投影数据。启动它还需要分发方提供页面与 `_framework/`；没有 WASM 产物的空页面不能算联调成功。网页必须通过 HTTP(S) 提供，不能直接用 `file:` 打开。真实准入票来自同源 launch 接口，不放查询参数。

Hello 静态页面与 Hello Bot 是独立的教学/测试协议路径，不能替代正式 DS 准入。现有公开示例的 [完整启动器说明](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/integration/README.md) 仍列有未公开的平台和启动依赖；不要把 `node integration/launcher.mjs --bots 2` 宣称为外部用户已可一键运行。
