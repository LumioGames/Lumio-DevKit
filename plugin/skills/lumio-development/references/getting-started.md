# 环境与第一步

目标：取得可用的项目入口，确认开发环境和产物身份，再做第一次可验证改动。

## 1. 先确认拿到了什么

| 输入 | 用途 | 缺失时 |
| --- | --- | --- |
| 公开 LumioSample 模板 | 玩法声明、配置样例、测试和启动器 | 可以直接 clone |
| 匹配的 `Lumio.Engine.SDK` 包与依赖 | 构建 C# 玩法，携带 Native 及公开使用说明 | 向发行方取得分发物或 feed；不临时实现引擎接口 |
| DS 分发物及匹配 Bot/客户端产物 | 真正启动双端 | 可以阅读与做局部工具验证，不能宣称双端跑通 |
| 账号服务配置与自己的测试账号 | 换取真实准入票 | 不在示例中自行伪造生产票据 |

2026-09-14 查询公共 NuGet `lumio.engine.sdk` 索引返回 404。模板当前使用 `0.1.0`，这不是已发布到公共 feed 的证明。需要分发物的步骤在取得它后执行；不要求外部使用者 clone 私有引擎源码。

开发环境按项目 `global.json`、依赖与工具声明安装：核对版本的 Sample 使用 .NET 10，Node 启动脚本使用 Node 22，配表 CLI 使用 Python 3.11+。Rust 编译器不是使用已分发 SDK 的默认前提。

```sh
dotnet --version
node --version
python3 --version
```

这些命令只确认工具可调用，不证明游戏能运行。

## 2. 取得模板

```sh
git clone https://github.com/LumioGames/LumioSample.git my-game
cd my-game
git rev-parse HEAD
```

先保留模板名称完成第一轮验证。重命名项目时再一起修改程序集名、namespace、生成器配置、测试引用和服务器程序集路径，避免只改文件夹名。

有 SDK 本地 feed 后，在项目目录执行（把路径换成实际分发目录）：

```sh
dotnet restore LumioSample.slnx -p:LumioLocalFeed=/absolute/path/to/feed
dotnet build LumioSample.slnx --no-restore -p:LumioLocalFeed=/absolute/path/to/feed
dotnet test LumioSample.slnx --no-build -p:LumioLocalFeed=/absolute/path/to/feed
```

Windows 同样传 `-p:LumioLocalFeed=C:/path/to/feed`。保留已有 NuGet 源以便解析其它依赖；feed 不只包含一个名字正确但依赖不全的 zip。模板会探测同级源码目录；要验证外部包路径，使用没有同级引擎源码的独立目录，并检查输出确实采用包依赖。

核对版本的模板只有在识别到本地 feed 中的 SDK nupkg 或已恢复的 SDK 包时才注入包引用；不能假定加一个空 feed 就能首次从网络恢复。模板给出 `LUMIO_SDK_UNRESOLVED` 时按报错确认实际文件、包版本和目录。

成功标准：restore/build 退出 0、测试实际发现并执行用例、输出目录包含配置与实际宿主需要的程序集。禁止以“输出目录里已有 DLL”代替本次构建成功。

**本次试跑的具体限制：**模板 `b236d2e` 与本机缓存的 SDK `0.1.0` 组合 restore 成功，但 build 报 `NETSDK1022`，三个生成的配置 Reader 被重复计入编译。该缓存包仅包含 SDK targets，缺少模板预期的 props；这不是所有同版本包都已证明会失败。请取得与模板匹配的完整分发组合并重新验证，不手改生成文件或关闭默认编译项来制造成功。包哈希与验证范围见 [验证记录](../../../VERIFICATION.md)。

## 3. 做第一个小改动

建议先在 Sample 的聊天服务器实现中调整一条日志文案，保留共享 RPC 签名，然后重新构建。具体入口见 [项目布局](project-layout.md)。

- 构建成功：只证明该端源码和生成结果可编译。
- 单元测试成功：只证明测试覆盖的逻辑。
- 启动 DS 与两个客户端后发送消息，发送方、服务器、接收方均有对应记录：才证明这次聊天链。

需要真实运行时转到 [服务器](../../lumio-server/SKILL.md) 与 [客户端](../../lumio-client/SKILL.md)。首次准备双端环境不要同时改 SDK 版本、协议与玩法，先建立可对比的运行基线。

## 4. 找公开 API

SDK nupkg 中的 `content/docs/public-api.md`、`content/docs/error-codes.md`、`content/wire/` 与 `lib/` 下 XML 是包使用面的参考。可用归档工具查看 nupkg，不修改缓存中的文件。程序集文件名中带 `NativeLoader` 不代表应手写 P/Invoke 或直接改函数表。

以拿到的包版本核对入口与示例；缺某接口时明确记录差异，不能凭另一个版本的签名猜调用。

## 来源与验证范围

- [Sample 的依赖与生成配置](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/Directory.Build.targets)
- [Sample 工具版本](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/global.json)
- SDK 公开可获取性查询：2026-09-14；后续以发行方实际分发为准。
- 本手册的具体执行证据见 [验证记录](../../../VERIFICATION.md)。本页不声称完整 Sample 场景已通过。
