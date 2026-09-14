# 服务器日志与排障

## 固定本次证据

保存当前命令、退出码、配置副本（删除敏感材料）、分发版本和 Native 身份。通用核对见 [诊断](../../lumio-development/references/diagnostics.md)。排障先找第一条失败，不立即重启；超时后某个有副作用操作是否完成可能未知。

日志目录相对配置文件解析，文件名为 `yyyy-MM-dd_序号.log`。Rust 与托管日志由同一个 DS 出口汇集，行包含 `tick`、`world`、`lang=rs/cs`、`target` 和消息。房间字符串可能位于消息的具名字段中，数值 `world=0` 不是“没有世界”的充分证据。

```sh
rg 'host.admit|host.drop|host.expire|host.faulted' logs
rg 'DS_FATAL|DS_READY|DS_CHECKPOINT|DS_DRAINING|DS_STOPPED' .run/ds-console.log
```

第二条假设本次已将控制台输出保存到指定文件；Host 的滚动日志不保证包含每一条控制台状态行。分享前去除账号口令、房间票、`Authorization` 与带票的子协议头。

`logging` 的有效配置：`dir` 非空；`min_level` 为 `trace/debug/info/warn/error`；`file_size_mb` 为 1–1024；`retention_days` 为 1–365；`mailbox_capacity` 为 64–1048576。要看 `host.tick` 时临时用 debug。邮箱是有界的，满时会丢日志并计数；日志缺行不能反向证明操作没发生。

## 先解释退出状态

| 退出码 | 含义 | 下一步 |
| --- | --- | --- |
| 0 | 配置检查成功，或运行最终保存和清理成功 | 分清执行的是 `--check-config` 还是实际运行；运行收尾应有 `DS_STOPPED`。 |
| 2 | 启动、运行或清理失败 | 保存 `DS_FATAL <code> <detail>`，从首个错误继续定位。 |
| 3 | 用法或配置拒绝 | 核对字段、范围、路径基准与实际分发模板。 |
| 4 | 启动或清理被期限监督终止 | 保存 stderr 阶段与超时值；尾部日志可能来不及落盘。 |

`DS_DRAINING` 仅说明已开始排空；`DS_CHECKPOINT` 仅说明一次检查点发布。两者均不能代替最终退出状态。

## 常见错误与具体检查

| 现象/稳定码 | 如何定位 |
| --- | --- |
| `configuration rejected` / `unknown field` | 从完整 detail 找键名；旧 `content_fingerprint`、`host.tick_hz` 与旧 durability 词不能继续使用。 |
| `logging_*` 配置错误 | 对照五个日志键的取值；缺整段也会拒绝，不能删掉日志段绕过。 |
| `sdk_version_mismatch` | Host 与 Native 的 ABI、BuildId 或托管发布不一致；取得兼容完整输出集，不能改 sidecar 的声明值。 |
| `sdk_load_failed` | 文件/sidecar、二进制哈希、平台架构或必要入口失败；保存 detail 和实际文件哈希。 |
| `clr_host_start_failed` | 核对 hostfxr、HostEntry DLL/runtimeconfig 和 .NET 架构；游戏 DLL 不是 CLR HostEntry。 |
| `registry_required` | 检查三份托管程序集路径与生成注册表。若明确报 `sdk_version_mismatch`，先修发布组合而非重写注册表。 |
| `config_load_failed` | 保留 detail 中的 Runtime 错误，如 `MANIFEST_NOT_FOUND`、`TABLE_CONTENT_FINGERPRINT_MISMATCH`、`DUPLICATE_ROW_ID`；重新生成/提供正确 export。 |
| `REVISION_FINGERPRINT_MISMATCH` | export 的 revision 与指纹不一致；不要手改清单哈希掩盖产物不一致。 |
| `S_PROJECTION_NOT_ON_DISK` | 核对 export 中服务器投影路径受限且文件存在；不是服务器源码目录。 |
| `voxel_world_unavailable` | `runtime+voxel` 未获得真正体素世界，检查 Native 与 Simulation net10.0 产物和绑定失败 detail。 |
| `checkpoint_incomplete_group` | 检查同一 generation 的 Runtime/Voxel 两半和清单；不要拼不同组或改 runtime-only。 |
| `checkpoint_corrupt_manifest` | 比对发布、房间、底图及内容身份，保留损坏原件；未经明确恢复安排不要删除、跳过或修写清单。 |
| `durability_profile_unsupported` | 当前 OS 不支持请求档位；选择较弱档位会改变承诺，不能静默降级。 |
| `connection_timeout` / `queue_full` | 对齐账号、连接代次、入站/出站配额与 owner 进度；先确认单次输入失败范围，再调整测试负载。 |

## 进程活着却没有 Ready

查看 `DS_FATAL` 的阶段，例如 `verifying_native_sdk`、`reading_content_fingerprint`、`recovering_checkpoint_store`、`starting_clr_runtime`。`host.owner_cold_start_timeout_ms` 默认 30000，稳态 `owner_call_timeout_ms` 默认 2000；冷启动预算应不小于稳态。先确认慢在哪，不能直接无限提高期限。

当前读配置和安装日志出口发生在部分启动监督之前；挂载或日志目录阻塞仍可能没有及时退出。记录卡住路径与进程状态，报告这一限制。不要把没有 Fatal 等同于健康。

## Ready 后进不了房或操作失败

检查客户端是否使用 launch 房间票而非普通账号凭证，再核对 allocation 六个维度、验签公钥和期限。服务端对每个 socket 验证；相同账号被接管后原连接应停止操作，不能复用旧输入重发。

准入成功后仍需检查 Self、初始世界提交和操作回执。普通权限/业务拒绝应只影响当前操作；若日志显示世界或会话因此 Faulted，记录为错误升级缺陷，不通过捕获所有异常继续伪造成功。当前部分待修路径可能尚不满足该语义。

停机与恢复问题先保留原目录。当前启动自动读取检查点及损坏组回退行为见 [开发与验证](development.md)；指南不添加自动重启/恢复循环。发布包若没有 `sdk-version.json`，托管程序集对 SDK 发布的核对会弱于完整分发身份检查；缺少该文件不能声称已经获得完整一致性证明。
