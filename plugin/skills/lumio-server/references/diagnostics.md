# 服务器日志与排障

本文按 Engine v0.0.2 的 DS、Host 和托管启动契约排障。先保存本次命令、退出码、Sample/Engine 版本、目标端、Native 身份以及失败前后的原始日志；去掉账号密码、准入票、`Authorization` 和完整用户数据。排障先找第一条失败，未知结果不要靠重复输入猜测。

## 先收集可复核证据

日志目录相对 `Server/Config/Startup/server.json` 解析。前台启动时把控制台输出保存到工作目录之外的受控文件，再执行：

```sh
rg 'host.admit|host.drop|host.expire|host.faulted' logs
rg 'DS_FATAL|DS_READY|DS_CHECKPOINT|DS_DRAINING|DS_STOPPED' .run/ds-console.log
```

`DS_READY` 才表示服务可接受新连接；端口已监听不能替代它。`DS_DRAINING` 只表示开始排空，`DS_CHECKPOINT` 只表示一次检查点发布，两者都不能替代最终的 `DS_STOPPED` 与进程退出码。日志缺行不能反向证明操作没有发生；记录每次命令的退出码和首个错误 detail。

## 常见关闭原因与错误码

DS WebSocket 关闭原因及数值来自 Engine v0.0.2 的 [`web/ds-close-codes.mjs`](https://github.com/LumioGames/LumioEngineRelease/blob/v0.0.2/web/ds-close-codes.mjs)；体素和持久化错误码来自 [SDK v0.0.2 包内的 `content/docs/error-codes.md`](https://github.com/LumioGames/LumioEngineRelease/tree/v0.0.2/sdk)。`config_load_failed`、`sdk_load_failed` 等行明确标为 Sample/Host 诊断，不把它们冒充 SDK 公共错误码。每行都保留原始码，再按下表处理。业务拒绝应留在操作回执；只有传输层明确要求时才关闭连接。

| 症状 | 关闭原因或错误码 | 含义 | 怎么办 |
| --- | --- | --- | --- |
| 刚连接就被拒绝 | `not_serving` (1013, DS) | 宿主尚未进入服务中，启动期新连接无会话 | 等待 `DS_READY`；启动器按有限次数重取同一张 launch 票。服务已经 Ready 后仍出现该码，应记录为 DS 契约问题。 |
| 准入容量暂满 | `admission_capacity` (1013, DS) | 服务已启动，但准入容量或 Owner 连接事件队列已满 | 稍后按有限退避拿新端点/票重试；不要把它当票格式错误。 |
| 服务中无法建立会话 | `admission_refused` (1008, DS) | 票、房间或 Runtime 准入条件不成立 | 检查 allocation、票的房间与期限和绑定字段；本次失败不要重放旧票。 |
| 输入或握手格式错误 | `bad_envelope` (1008, DS) / `protocol_violation` (1008, DS) | 帧无法解码、超出大小，或违反握手/消息顺序 | 保存关闭前的原始帧类型与客户端版本，修正发送端；不要通过截断或忽略字段继续。 |
| 空闲或握手超时 | `connection_timeout` (1008, DS) | 连接未在协议时限内完成阶段，或超过空闲期限 | 核对网络、握手阶段和连接代次；确认是超时还是服务端故障后再建立新连接。 |
| 入站或出站背压 | `queue_full` (1009, DS) / `send_buffer_overflow` (1009, DS) | 有界队列或发送缓冲达到上限 | 降低测试负载并检查消费进度、Owner 队列和客户端读取速度；不要静默丢弃操作。 |
| 房间运行中断开 | `internal_error` (1011, DS) | 服务端内部故障，不是普通业务拒绝 | 保存 `DS_FATAL`、Host/Native 身份和首个错误 detail；停止输入，修复兼容发布物后重现。 |
| 正常退出或维护 | `shutdown` / `normal_logout` / `session_closed` (1000, DS) | 对端按协议结束会话 | 检查是否有 `DS_STOPPED`、最终 checkpoint 和退出码；不要对正在关闭的房间自动重连。 |
| 新连接被替换 | `superseded` (1000, DS) | 同一账号或连接代次被后续会话接管 | 记录连接代次与准入时间，只保留最新会话；不要复用旧输入。 |
| Host 与 Native 不匹配 | `sdk_version_mismatch` (SDK) | ABI、BuildId、sidecar 或托管发布不属于同一个 Engine v0.0.2 组合 | 保存完整身份字段和哈希，重新取得同一发布组合；不能改 sidecar 声明值掩盖不一致。 |
| Native 装载失败 | `sdk_load_failed` (Sample/Host) | 文件、sidecar、平台架构、二进制哈希或入口检查失败 | 保存 detail、实际文件哈希和目标 RID，修复发布包后重试。 |
| CLR 宿主未启动 | `clr_host_start_failed` (Sample/Host) | hostfxr、runtimeconfig、架构或入口程序集不满足启动条件 | 核对 `Lumio.Server.HostEntry.HostEntry, Lumio.Server.HostEntry` 和 `LumioHostEntry`，确认入口来自 Engine 发布物。 |
| 注册表缺失 | `registry_required` (Sample/Host) | 托管程序集没有提供生成的注册表，无法建立类型/协议映射 | 检查 `Gameplay/` 的 server/client 构建输出及生成注册表；不要以手写临时映射替代发布物。 |
| 配置或内容加载失败 | `config_load_failed`、`MANIFEST_NOT_FOUND`、`TABLE_CONTENT_FINGERPRINT_MISMATCH`、`DUPLICATE_ROW_ID` (Sample/Host；本轮未执行 Loader 实例复测) | 配置、export 根或表内容与清单不一致 | 从同一源重新导出并生成 Reader，核对 `Server/Config/Startup/server.json`；不要手改清单哈希。 |
| 体素世界不可用 | `voxel_world_unavailable` (Sample/Host) | Runtime 没有获得真正的体素世界或 Host 绑定失败 | 检查 Engine v0.0.2 Native、Simulation net10.0 产物及绑定 detail；把本次操作标为未完成，不把缺失世界当空气。 |
| 检查点不成组 | `checkpoint_incomplete_group` | 同一 generation 缺少 Runtime/Voxel 半边或清单记录 | 保留原存储和日志，核对发布、底图、表清单与 generation；不要拼接不同组。 |
| 检查点清单损坏 | `checkpoint_corrupt_manifest` | 检查点身份、哈希或清单不可验证 | 保留损坏原件，按恢复计划处理；不要删除最新组或手改清单“修复”。 |
| 持久化档位不支持 | `durability_profile_unsupported` | 当前 OS/存储不支持请求的 durability 档位 | 选择经过评估的档位并记录承诺变化；禁止静默降级。 |

## 进程活着却没有 Ready

查看 `DS_FATAL` 所在阶段，例如 `verifying_native_sdk`、`reading_content_fingerprint`、`recovering_checkpoint_store` 或 `starting_clr_runtime`。先确认卡在哪里，再调整超时；没有 Fatal 也不等于健康。若日志目录、挂载或 HostFXR 阻塞导致启动监督没有及时输出，记录进程状态和卡住路径，明确标记为“本次未验证”。

## Ready 后进不了房或操作失败

客户端必须使用 Platform 为当前房间签发的 launch 票，而不是普通账号凭证。核对 allocation 的六个维度、验签公钥和期限，再区分 socket、准入、Welcome、首帧和操作回执。相同账号被接管后，原连接应停止操作；不能用旧输入重发。

准入成功后继续检查 Self、初始世界提交和操作回执。若是普通权限或业务拒绝，只影响当前操作；若日志显示世界或会话因此 Faulted，按错误升级记录。停机和恢复先保留原目录，比较 `runtime+voxel` 同一 generation 的两半及底图/内容身份；未执行的恢复步骤写明“未执行”。

## 证据模板

```text
目标端与版本：
操作和输入（已去敏）：
预期 / 实际：
最早失败层与原错误：
DS/Host/Native/程序集身份：
重现命令与退出码：
已验证 / 未验证：
```

相关入口：[服务器配置](setup.md)、[开发与验证](development.md)、[通用分层诊断](../../lumio-development/references/diagnostics.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
