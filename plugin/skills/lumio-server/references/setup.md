# 搭建与配置 Dedicated Server

DS（运行游戏世界的服务器进程）从 Engine 发布物启动，加载游戏的服务端程序集、地图和配表。

## 准备与启动

前置条件是 Git、[global.json](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/global.json) 要求的 .NET SDK、Node.js 22 和 Docker；先按 [开始开发](../../lumio-development/references/getting-started.md) 获取带 `Engine/` 子模块的 Sample。Engine v0.0.2 提供 `win-x64` 和 `linux-x64` 两个平台的运行文件，RID（操作系统与处理器组合）须与本机一致。

在 Sample 根目录执行公开 [README](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/README.md) 中的命令（Apache-2.0）：

```sh
dotnet build LumioSample.slnx
dotnet build Gameplay/Lumio.Sample.Gameplay.csproj -p:LumioEcsSide=client
dotnet build Client/Bots/Lumio.Sample.Bots.csproj
node Tools/launcher.mjs --bots 2 --stagger-ms 250 --scenario-dll Client/Bots/bin/Debug/net10.0/Lumio.Sample.Bots.dll
```

启动器会核对 Engine 文件，准备 Platform（账号和房间服务）、生成本次配置、检查 DS 配置，再启动 DS 和 Bot（自动操作的客户端）。预期结果是十四步逐项有结果，最后输出 `VERIFICATION_STATUS` 和 `EVIDENCE_PATH`。查看其中的 `verification.json`，不要只看进程是否启动。

## 配置从哪里来

模板是 [Server/Config/Startup/server.json](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Server/Config/Startup/server.json)。其中的相对路径以配置文件所在目录为准。启动器会在 `.run/` 下生成本次配置，填入当前房间和票据对应的信息。

| 配置 | 内容与检查方法 |
| --- | --- |
| `allocation` | `serverAudience`、`gameId`、`gameReleaseId`、`contractId`、`roomId`、`allocationId` 应与 Platform 签发的房间票一致。 |
| `admission_key_id` / `admission_public_key_hex` | 验票的密钥编号与公钥；使用本次 Platform 的配置。 |
| `clr.entry_type` / `clr.entry_method` | `Lumio.Server.HostEntry.HostEntry, Lumio.Server.HostEntry` / `LumioHostEntry`。入口程序集来自 Engine 的 `server/<rid>/Application/`。 |
| `clr.registry_assembly` | 默认指向 `Gameplay/bin/Debug/net10.0/Lumio.Sample.Gameplay.dll`，即服务端玩法输出。 |
| `config_dir` | 默认解析到 `Server/Config/Tables/`，须有导出的 `manifest.json`。 |
| `world_profile` | `runtime+voxel`，同时使用实体和方块世界。 |
| `voxel_catalog` | `Server/Assets/Maps/official-catalog.json`，声明方块种类、形状和资源引用。 |
| `base_map_path` | `Server/Assets/Maps/sample.voxel`，与底图编号、版本、SHA-256 一起核对。 |
| `store_path` | 检查点（用于重启恢复的世界存档）目录；启动器每次导览创建新目录，第十四步复用同一目录。 |
| `durability` | Sample 使用 `snapshot_only`；检查点之间的操作不能仅凭这个设置推断已经持久保存。 |
| `logging` | 日志目录、最低级别、文件大小、保留天数和队列容量。 |

发布物中的 HostEntry 程序集名与 Sample 模板一致。v0.0.2 的 `server/` 目录没有随附启动配置样例；这是发布物的文档缺口，当前以公开 Sample 模板填写配置。

## 排查启动

[Tools/launcher.mjs](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Tools/launcher.mjs) 在启动前调用 `lumio-ds --check-config`。它检查配置，不代表实际装载程序集或地图成功；运行后出现 `DS_READY` 才能进入连接阶段。Windows 的文件名为 `lumio-ds.exe`。

缺少 Engine 文件时先补子模块；文件校验失败时重新取得匹配版本；平台不支持或缺 Docker 时补运行环境。具体日志与处理见 [服务器排障](diagnostics.md)，连接见 [客户端搭建](../../lumio-client/references/setup.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
