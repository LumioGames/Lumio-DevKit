# 日志与分层定位

先保存本次命令、退出码、Sample/Engine 版本、目标端和失败前后的原始日志。去掉账号密码、准入票、`Authorization` 和完整用户数据；不要用“进程被清理”证明步骤通过。

## 按症状查错误码

下面区分两类公开来源：DS WebSocket 关闭原因及数值来自 Engine v0.0.2 的 [`web/ds-close-codes.mjs`](https://github.com/LumioGames/LumioEngineRelease/blob/v0.0.2/web/ds-close-codes.mjs)，体素和持久化错误码来自 [SDK v0.0.2 包内的 `content/docs/error-codes.md`](https://github.com/LumioGames/LumioEngineRelease/tree/v0.0.2/sdk)。完整表以这两份发布物文件为准；看到新码时保留原文，不借用相近码。标为 Host/Sample 的名称不是 SDK 公共错误码。

| 症状 | 关闭原因或错误码 | 含义 | 怎么办 |
| --- | --- | --- | --- |
| 刚连接就被拒绝 | `not_serving` (1013, DS) | 宿主尚未进入服务中，启动期新连接无会话 | 先等 `DS_READY`；连接阶段按启动器的有限重试重取同一张 launch 票。已经 Active 后再收到它应报告 DS 契约问题。 |
| 准入容量暂满 | `admission_capacity` (1013, DS) | 服务已启动，但准入容量或 Owner 连接事件队列已满 | 稍后按有限退避拿新端点/票重试；不要把它当票格式错误。 |
| 房间运行中断开 | `internal_error` (1011, DS) | 服务端内部故障，不能把它当普通业务拒绝 | 保存 DS_FATAL、Host/Native 身份和首个异常；停止输入，修复兼容发布物后重现。 |
| 票过期或房间不匹配 | `protocol_violation` / `connection_timeout` (DS) | 准入字段、协议顺序或握手时限不满足 | 重新从 Platform 获取本房间新票，核对 allocation 六项和公钥；不要把账号登录凭据当 DS 票。 |
| 正常退出或维护 | `shutdown` / `session_closed` (1000, DS) | 对端按协议结束会话 | 检查是否有 `DS_STOPPED` 和最终 checkpoint；不要自动重连正在关闭的房间。 |
| 体素读不到 | `section_unavailable` / `pinned_read_returned_pending` (SDK) | Section 尚未就绪或驻留预算不足，结果不是空气 | 记录 Section key 和 revision，等待宿主驻留后重试当前操作；不要填 `BlockId=0`。 |
| 写入被并发拒绝 | `stale_section_revision` (SDK) | 提交使用的 Section 修订已过期 | 重新读取、重新判断权限和目标，再以同一业务操作身份排队；不要盲目换 revision 覆盖。 |
| 查询参数越界 | `coordinate_out_of_bounds` / `cell_offset_out_of_range` (SDK) | 世界坐标或 Section 内偏移不在契约范围 | 修正坐标映射和 `0..4095` 的 cell offset；保留原始码。 |
| 批量读写超额 | `read_budget_exceeded` / `write_batch_too_large` (SDK) | 一次调用超过发布物预算 | 拆小批次并记录预算；不要静默截断请求。 |
| 带存档起不来 | `checkpoint_corrupt_manifest` / `checkpoint_incomplete_group` | 检查点身份或 Runtime/Voxel 成套文件不完整 | 保留原存储和日志，核对发布、底图、表清单和 generation；按恢复计划处理，不删除最新组来“修复”。 |
| 配表加载失败 | `MANIFEST_NOT_FOUND` / `TABLE_CONTENT_FINGERPRINT_MISMATCH` (Host/Sample loader，本轮未执行 Loader 实例复测) | export 根缺文件或清单指纹与内容不一致 | 从同一源重新导出并重新生成 Reader；不要手改 manifest/hash。 |

浏览器显示的 1006 是浏览器报告的无 close frame，不是 DS 可以发送的服务端码。业务拒绝应留在操作回执，不应关闭整个房间。

## 分层定位

| 现象 | 先看 | 下一步 |
| --- | --- | --- |
| restore/build 失败 | 第一条编译错误、`Engine/manifest.json`、目标框架 | 先补 Engine 子模块或修生成源，不启动旧 DLL。 |
| `LUMIO_SDK_UNRESOLVED` | `Engine/` 是否初始化、SDK nupkg 与 manifest 版本 | 运行 `git submodule update --init --depth 1 Engine`，确认版本后再构建。 |
| Native 装载失败 | Engine Release 的 RID、BuildId、sidecar 和哈希 | 取得完整 v0.0.2 组合；不要关闭身份检查或手改 sidecar。 |
| Native 成功但 CLR 未启动 | `Lumio.Server.HostEntry.HostEntry`、`LumioHostEntry`、runtimeconfig 和 hostfxr | 对照 [服务器配置](../../lumio-server/references/setup.md)，确认 HostEntry 来自 Engine 发布物。 |
| 能连但进不了房 | launch 票、allocation 六项、`DS_READY` 和连接代次 | 区分 socket、准入和首帧；不要重复使用旧票。 |
| 入场后没有实体/聊天 | 服务器入队、Tick、复制、客户端应用和表现日志 | 用同一操作 ID 逐段对齐；本地 UI 成功不能替代权威结果。 |
| 方块或物理查询失败 | `Presence`、`HasBlockId`、`Unresolved` 和宿主绑定 | 转 [体素指引](../../lumio-voxel/SKILL.md)，不要把缺块当空气。 |

## 证据模板

```text
目标端与版本：
操作和输入（已去敏）：
预期 / 实际：
最早失败层与原错误：
DS/Client/Native/程序集身份：
重现命令与退出码：
已验证 / 未验证：
```

限制要明确写成“能力不存在”“尚未接线”“缺运行环境”或“本次未验证”中的一种。更多 DS 日志字段和存档定位见 [服务器诊断](../../lumio-server/references/diagnostics.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
