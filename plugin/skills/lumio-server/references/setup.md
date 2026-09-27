# 搭建与配置 Dedicated Server

## 前置产物

本指南按 `LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb` 与 Engine v0.0.2 核对。公开 Sample 通过只读 `Engine/` 子模块取得一整套引擎发布物，不要求访问私有仓库。前置条件是 git、项目 `global.json` 要求的 .NET SDK、Node.js 22 和 Docker（本地 Platform）。

Engine v0.0.2 的发布物包含 SDK 包、`server/<rid>/lumio-ds`、`server/<rid>/Application/`、`server/<rid>/SDK/Managed/`、`server/<rid>/SDK/Native/<rid>/`、Bot 宿主、Web 共享零件和 Platform compose。先确认 `Engine/manifest.json` 的版本和本机 RID，再运行：

```sh
node Engine/tools/verify-release.mjs --root Engine --rid <rid>
```

缺少子模块时补拉：

```sh
git submodule update --init --depth 1 Engine
```

验证脚本返回 exit 1 时记录 `sdk_version_mismatch`/发布物不一致并停止；缺少发布物或 manifest 没有本机平台（exit 2）才记录 `BLOCKED_ENV`。不拿其他平台凑运行条件。

## 从 Sample 模板开始

Sample 的运行模板是 [`Server/Config/Startup/server.json`](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Server/Config/Startup/server.json)。相对路径均以该文件所在目录为基准；本地覆盖写入已忽略的 `.run/`，不要改提交的模板来放凭据。

| 配置 | 如何填写/核对 |
| --- | --- |
| `allocation` | Platform/运维分配的 `serverAudience`、`gameId`、`gameReleaseId`、`contractId`、`roomId`、`allocationId`，与房间票一致。 |
| `admission_key_id` / `admission_public_key_hex` | 对应 Platform 签发密钥；公钥为 32 字节的 64 位十六进制文本。不能把测试值作为真实验签配置。 |
| `clr.entry_type` / `clr.entry_method` | Engine v0.0.2 的入口是 `Lumio.Server.HostEntry.HostEntry, Lumio.Server.HostEntry` / `LumioHostEntry`。 |
| `clr.registry_assembly` | 本次构建的 `Gameplay/bin/<Configuration>/net10.0/Lumio.Sample.Gameplay.dll`；不要指向客户端输出。 |
| `config_dir` | `Server/Config/Tables/` 或相同发布生成的 export 根，必须含 `manifest.json`。 |
| `world_profile` | Sample 使用 `runtime+voxel`；缺少体素世界时不要改成 `runtime-only` 掩盖缺件。 |
| `store_path` | 当前房间的新检查点目录；复用旧目录会触发启动恢复。 |
| `base_map_id` / `base_map_version` / `base_map_content_sha256` | 与 `Server/Assets/Maps/sample.voxel` 及其版本和 SHA-256 一致。哈希字段不等于底图已加载。 |
| `durability` | Sample 使用 `snapshot_only`；不能凭名字推断逐操作 WAL。 |
| `logging` | 填写 `dir`、`min_level`、`file_size_mb`、`retention_days`、`mailbox_capacity`。 |

`Gameplay/` 是两端共享玩法；`Server/` 只放服务端配置、配表、地图和测试；引擎宿主和 Native 从 `Engine/server/<rid>/` 取。缺少 `Lumio.GameRuntime.Simulation.dll` 或 `DedicatedServerHostBinding` 时报告缺件，不制造替身。

## 校验与启动

下例在 Sample 根目录执行：

```sh
node Engine/tools/verify-release.mjs --root Engine --rid <rid>
node Tools/launcher.mjs --bots 2 --stagger-ms 250 --scenario-dll Client/Bots/bin/Debug/net10.0/Lumio.Sample.Bots.dll
```

`Tools/launcher.mjs` 会按十四步导览准备 Platform、DS 和 Bot。只要依赖不齐就逐步打印 `BLOCKED_ENV` 并点名路径；没有完整分发物时不要启动替代服务器制造通过。

若需单独检查 DS，使用发布物中的 `lumio-ds` 和 Sample 的配置模板：

```sh
Engine/server/<rid>/lumio-ds --config Server/Config/Startup/server.json --check-config
Engine/server/<rid>/lumio-ds --config Server/Config/Startup/server.json
```

第一条只校验 JSON 字段、范围与配额关系；第二条需要出现 `DS_READY` 才能继续连接。端口已监听不能替代 Ready。真实准入必须使用 Platform 签发的房间票，不把票放入 URL、版本库或示例命令文本。

公开阅读：[Sample README](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/README.md)、[启动模板](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Server/Config/Startup/server.json)、[一键启动器](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Tools/launcher.mjs)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
