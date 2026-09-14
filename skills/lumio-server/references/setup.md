# 搭建与配置 Dedicated Server

## 前置产物

本指南核对日期为 2026-09-14。SDK 包取得见 [开始开发](../../lumio-development/references/getting-started.md)。还需要分发方交付目标 OS/架构的 `lumio-ds`、Native 库与身份 sidecar、托管 HostEntry 及运行配置、匹配的 .NET/hostfxr。它们不能由“已有游戏 DLL”推断存在。

另需服务器侧游戏程序集及配套 Runtime 依赖、生成注册表、编译后的配置 export、底图/存储方案，以及平台给出的 allocation 和准入验签公钥。不要用客户端拿到的票反向编造服务器身份。缺少 DS 或平台分发时，可以完成游戏编译和配置审阅，真实运行应标记受阻。

## 从分发模板开始

在分发目录复制随包的 `server.example.json` 为本次运行的 `server.json`。公开 [Sample 配置样本](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/server.sample.json) 可用来理解配置用途，但不能原封不动启动：它包含待替换的房间身份和公钥，部分 CLR 路径也必须按实际 Host 产物修正。

所有相对路径以 **server.json 所在目录** 为基准；移动配置文件后要重新检查路径。

| 配置 | 如何填写/核对 |
| --- | --- |
| `allocation` | 平台/运维分配的 `serverAudience`、`gameId`、`gameReleaseId`、`contractId`、`roomId`、`allocationId`，与房间票一致。 |
| `admission_key_id` / `admission_public_key_hex` | 对应平台签发密钥；公钥为 32 字节的 64 位十六进制文本。不能把测试值作为真实验签配置。 |
| `clr.engine_native` / `clr.hostfxr` | 当前平台的 Native 引擎与 .NET hostfxr 文件。 |
| `clr.assembly` / `clr.runtime_config` | 分发包实际的 `Lumio.Server.EntityChat.HostEntry.dll` 与对应 runtimeconfig；不能因为游戏 DLL 存在就将其用作 HostEntry。 |
| `clr.entry_type` / `clr.entry_method` | 当前 HostEntry 是 `Lumio.Server.EntityChat.HostEntry.HostEntry, Lumio.Server.EntityChat.HostEntry` / `LumioEntityChatEntry`。 |
| `clr.replication_assembly` / `clr.ecs_assembly` / `clr.registry_assembly` | 同一兼容发布的 Runtime Replication、Ecs 与服务器玩法注册表程序集；不要指向客户端输出。 |
| `config_dir` | LumioConfig export 根，包含 `manifest.json`；`contentFingerprint` 从清单读取，不手填 `content_fingerprint`。 |
| `world_profile` | 显式为 `runtime-only` 或 `runtime+voxel`；Sample 使用后者，缺体素接入不能用改 profile 掩盖。 |
| `store_path` | 当前房间的检查点目录。首次试跑用明确的新目录；已有目录会触发当前程序的启动恢复路径。 |
| `base_map_id` / `base_map_version` / `base_map_content_sha256` | 与实际底图一致的身份和 SHA-256。哈希字段不等于底图文件已被加载；保留内容的实际装载证据。 |
| `durability` | `snapshot_only`、`async` 或 `durable`；当前以检查点组为单位，不能据名字推断逐操作 WAL 已接通。`durable` 的支持受平台限制。 |
| `logging` | 五键均填写：`dir`、`min_level`、`file_size_mb`、`retention_days`、`mailbox_capacity`。具体范围见排障文档。 |

`runtime+voxel` 的托管输出还需包含 net10.0 的 `Lumio.GameRuntime.Simulation.dll`，提供 `DedicatedServerHostBinding`。若分发物缺失，报告缺件；不能用不含该类型的程序集或虚构句柄替代。

## 校验与启动

下例在已解包的 DS 目录执行。Windows 使用对应 `.exe`；路径必须根据实际分发包调整。

```sh
./lumio-ds --config server.json --check-config
./lumio-ds --config server.json
```

第一条预期打印 `configuration_valid` 并退出 0。它只校验 JSON 字段、范围与配额关系，不打开配表、加载 Native 或验证程序集。多余/旧键会被拒绝，例如 `content_fingerprint`、`host.tick_hz`。

第二条会创建日志并初始化运行环境。只有出现 `DS_READY` 才能继续连接，核对 JSON 中 `endpoint`、`roomId`、`gameReleaseId`、`tickRate`、`worldProfile`、`contentFingerprint`；`listen_port=0` 时使用它实际报告的端口。TCP/WS 端口已监听不能替代 Ready。

初次本地运行保留 loopback 监听。真实 Native/Bot 在 WebSocket Upgrade 中提交 `Authorization: Bearer <房间准入票>`；浏览器使用提供的适配器，以 `lumio-admission.<票>` 子协议 offer 携带票，服务端仅选择 `lumio.mvp.v0`。不要在 URL 传票。普通账号登录凭证尚未绑定房间，不能用于 DS 准入。

## Hello 不等于正式 DS

Hello/replay/免认证 observer 属于显式测试 harness。看到 Hello 文本往返，不表示当前游戏的注册表、平台验票或 `runtime+voxel` 已工作。公开 [Sample 启动器](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/integration/README.md) 还依赖未公开的环境，当前不能承诺从公开 clone 一键完成十四步。缺件就停在具体步骤，不启动替代服务器制造通过。
