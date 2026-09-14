# 客户端日志与排障

先保存本次命令（去除票和密码）、退出码、Host/SDK/游戏版本和独立日志目录。通用证据与 Native 身份核对见 [诊断](../../lumio-development/references/diagnostics.md)。

## 先确定卡在哪一层

| 证据 | 已证明 | 尚未证明 |
| --- | --- | --- |
| `admission-events.ndjson` 的 `started` | Bot 进程启动 | Socket、验票和世界 |
| `connected` | 握手已接受，进入同步 | 初始副本已提交 |
| `admitted` | Session 进入 Active | 某次游戏操作成功 |
| `result.ndjson` 的 `issue.accepted=true` | 输入出口接收请求 | 已发出或已被 DS 应用 |
| `uplinks` 增长 | 会话实际产生上行 | 权威提交及其他玩家看见 |
| 第二客户端出现目标聊天/状态 | 下行消费成功 | 全部玩法、存档和重启正确 |

常驻 Bot 使用 `--log-dir` 下的 `yyyy-MM-dd_序号.log` 保存生命周期；场景额外写 `result.ndjson`。不能假设不同入口都有完全相同的日志文件。

```sh
rg 'session state changed|session_faulted|superseded|cadence.rejected' .run/bot01
rg '"kind":"(vocabulary|issue|assert|run)"' .run/chat-once/result.ndjson
```

常驻日志旋钮：`--log-min-level`、`--log-file-size-mb`、`--log-retention-days`、`--log-mailbox-capacity`；环境键分别为 `LumioBotLogMinLevel`、`LumioBotLogFileSizeMb`、`LumioBotLogRetentionDays`、`LumioBotLogMailboxCapacity`，目录键为 `LumioBotLogDir`。先临时升到 `debug` 重现一次，再收窄；不要靠无限增大日志队列掩盖阻塞。

## 常见失败

| 现象/码 | 检查与下一步 |
| --- | --- |
| `LUMIO_SDK_UNRESOLVED` | SDK feed/缓存尚未就绪；按通用搭建取得完整包，不补私有路径或删闸门。 |
| `GAMEPLAY_ASSEMBLY_NOT_FOUND` / 20 | 核实 `--gameplay` 是当前客户端输出 DLL。 |
| `SCENARIO_ASSEMBLY_NOT_FOUND` / 21 | 核实场景文件与依赖实际存在。 |
| `GAMEPLAY_REGISTRY_MISSING` / 22 | 检查生成是否执行、侧别和依赖版本；不要手造“全部实体都存在”的注册表。 |
| `SCENARIO_TYPE_NOT_FOUND` / 23 | 传完整命名空间与类名。 |
| `SCENARIO_TYPE_INVALID` / 24 | 类型应可创建并实现相同发布的 `IBotScenario`。 |
| `CAPABILITY_MISMATCH` / 25 或能力 `BLOCKED` / 8 | 比对 `RequiredCapabilities` 与实际词表；报告缺失能力。 |
| `BLOCKED` / 8，缺连接材料或 Native | 核对 `--server`、票环境变量、Native 路径与对应 sidecar；不要切到 fixture 伪装生产通过。 |
| `no_uplink_channel` | 使用了无宿主输入出口的 context；交给真实 Host 创建场景上下文。 |
| 输入被拒绝但界面无提示 | 记录 `BotIssueResult.Reason` / `BlockedReason`；当作该操作失败，别反复发送。 |
| 常驻连接后没有消息 | 先检查 Active、Self 和 `InputEnabled`，再看实际词表与上行；不要仅观察进程 CPU。 |
| 浏览器白屏/空点图 | 核对 HTTP 服务、WASM `_framework/` 是否加载、launch/WS 请求和实际 C# 副本输出；缺产物不能当作空世界。 |

## 断线与拒绝

普通操作拒绝与会话数据损坏是不同问题。拒绝应有明确结果，并允许后续合法操作继续；若 SDK 把普通拒绝升级为世界故障，保留首次错误、输入和前后 Tick，报告缺陷，不在游戏侧吞异常或重置世界。

现有生产 Bot 在普通网络断开后可能尝试从平台重新取票，相关环境包括 `LUMIO_PLATFORM_ORIGIN`、`LUMIO_GAME_SLUG`、`LUMIO_ACCOUNT_PASSWORD` 及 Bot 工具凭据。这是当前宿主行为，不是本指南建议的恢复策略；缺少这些材料也不等于存在受支持的“禁用重连”开关。若任务要求断线即停，现有 CLI 的行为需先满足该要求，不能宣称已经可配置。

被同账号接管或数据应用失败后，保存原因并结束本次实验；不要自动重放旧输入。自建 Host 调用 `IClientSession.Dispose()` 后仍需在原 owner 循环继续 Tick，读取快照 `CleanupStatus` / `IsDisposed` 确认释放完成，再释放 Native 资源。不得用跨线程补 Tick 或直接卸载 Native 库处理卡顿。
