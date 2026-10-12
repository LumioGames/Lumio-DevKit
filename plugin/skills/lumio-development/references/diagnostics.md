# 日志与分层定位

从玩家看到的症状找到最早失败的一层，保留关闭原因、错误码和前后的日志。

## 按症状查错误码

完整码表在 [Engine v0.0.2 SDK 包](https://github.com/LumioGames/LumioEngineRelease/raw/refs/tags/v0.0.2/sdk/Lumio.Engine.SDK.0.0.2.nupkg) 内：用 ZIP 解压工具打开，阅读 `content/docs/error-codes.md`；WebSocket 的完整关闭原因、数值和处理动作在 `content/wire/ds-transport-v1.json` 的 `closeCodes` 中。关闭码映射也可直接浏览发布物的 [`web/ds-close-codes.mjs`](https://github.com/LumioGames/LumioEngineRelease/blob/v0.0.2/web/ds-close-codes.mjs)。以下只选常见症状。

| 症状 | 关闭原因或错误码 | 什么意思 | 怎么办 |
| --- | --- | --- | --- |
| 刚连接就被拒绝 | `not_serving`，1013 | 服务器仍在启动，这个连接尚未进入房间 | 等待 `DS_READY`；连接阶段按客户端已有逻辑有限退避重试同一地址，超限后报告失败。 |
| 房间暂时挤不进去 | `admission_capacity`，1013 | 服务器正在服务，但待准入数、房间数或连接事件队列达到上限 | 连接阶段有限退避重试同一地址；持续失败时查服务器容量，不把它当票格式错误。 |
| 票过期或房间不匹配 | `admission_refused`，1008 | 本次准入被拒绝，具体原因在服务器准入日志里 | 结束本次尝试，不用同一张票自动重试；核对房间与凭证，重新走平台进房流程。 |
| 被同账号的新连接踢出 | `superseded`，1000 | 新连接取代旧连接 | 提示账号已在别处连接，不自动重连争抢会话。 |
| 发送消息后被断开 | `protocol_violation`，1008 | 帧类型或握手顺序不符合协议 | 保存原始原因与客户端版本，修复协议用法；不自动重连掩盖错误。 |
| 长时间无响应后断开 | `connection_timeout`，1008 | 空闲超时，服务器未收到入站帧或心跳回复 | 查网络与心跳；按客户端恢复流程取得新地址和新票后重连。 |
| 房间运行中出现服务端故障 | `internal_error`，1011 | 连接或世界因内部故障不能继续 | 保留第一条故障日志和发布物版本，按服务端故障处理，不当普通断线或业务拒绝。 |
| 正常结束或关服 | `shutdown` / `session_closed`，1000 | 进程正在关服，或会话已结束 | 不自动重连；需要再次进入时回平台领取房间地址。存档结果另查关服日志。 |
| 体素暂时读不到 | `section_unavailable` | Section（16×16×16 格的体素分区）当前不可用 | 停止当前读写，核对分区是否已装载；不能把缺失数据填成空气。 |
| 已保证就绪的区域仍读不到 | `pinned_read_returned_pending` | 已完成 pin（要求区域保持可用）后仍返回 Pending 或 Unavailable，违反就绪保证 | 保留区域、版本和宿主日志，报告该故障；不能当正常等待继续写地形。 |
| 写地形被拒绝 | `stale_section_revision` | 写入带的分区版本已过期；存储回执也可能带了不匹配版本 | 对写入重新读取并重新判断目标后提交；对存储回执检查版本关系，不强改版本号覆盖。 |
| 坐标或格内偏移越界 | `coordinate_out_of_bounds` / `cell_offset_out_of_range` | 坐标不在允许范围，或格内偏移不在 0–4095 | 修正坐标换算与范围检查后重新发起操作。 |
| 一次读写太多 | `read_budget_exceeded` / `write_batch_too_large` | 超过读取预算或整批写入条数上限 | 按发布物限制拆分业务批次；不得截断请求后声称整批成功。 |
| 带存档起不来 | `checkpoint_corrupt_manifest` / `checkpoint_incomplete_group` | 检查点清单损坏，或恢复所需的一组文件不完整 | 保留原存档、版本和第一条恢复错误，请维护者检查清单及配套文件；不要删除最新存档来掩盖失败。 |

客户端必须同时看数值和 reason（关闭原因字符串）：同为 1008，`connection_timeout` 可以恢复，`protocol_violation` 应报告协议问题。不认识的组合按故障记录。浏览器的 1006 表示没有收到有效关闭帧，不是服务器能主动发送的码。

上游参考已随包提供，但部分条目仍缺具体解释：`checkpoint_corrupt_manifest` 使用通用说明，`checkpoint_incomplete_group` 只列规则编号。这里只给保留数据和检查配套文件的处理方向，详细修复步骤属于上游文档缺口。

## 分层定位

| 现象 | 先看 | 下一步 |
| --- | --- | --- |
| restore/build 失败 | 第一条编译错误、`Engine/manifest.json`、`global.json` | 补齐所需工具或修复源文件，再重新构建。 |
| `LUMIO_SDK_UNRESOLVED` | `Engine/` 是否有 manifest 和 SDK 包 | 运行 `git submodule update --init --depth 1 Engine`。 |
| Native（原生库）装载失败 | 发布物支持的平台、身份信息与文件校验结果 | 按 [环境与第一步](getting-started.md) 取得完整匹配的发布物。 |
| Native 成功但托管入口未启动 | `Lumio.Server.HostEntry.HostEntry`、`LumioHostEntry` 和入口程序集 | 对照 [服务器配置](../../lumio-server/references/setup.md)。 |
| 能连但进不了房 | launch 票（房间准入凭证）、准入日志与 `DS_READY` | 先用上表区分准入拒绝、容量不足与协议问题。 |
| 入场后看不到实体或聊天 | 服务器收到输入、每帧处理、同步发送、客户端接收和显示 | 按 [同步与 RPC](../../lumio-gameplay/references/sync-and-rpc.md) 对齐同一消息。 |
| 配表加载失败 | 错误正文、目标端、实际导出根和清单 | 按 [配表更新](../../lumio-config/references/runtime-and-updates.md) 重新导出完整产物。 |
| 方块或物理查询失败 | 查询状态、分区是否可用和坐标 | 转 [体素指引](../../lumio-voxel/SKILL.md)。 |

## 保存可重现的记录

记录命令、退出码、Sample/Engine 版本、目标端、预期结果、实际结果和最早失败日志。去掉密码、准入票、`Authorization` 与完整用户数据。进程被强制清理不代表步骤成功。

日志里出现的错误码保留原样；更多服务器字段和存档定位见 [服务器诊断](../../lumio-server/references/diagnostics.md)。限制措辞见 [能力入口](capabilities.md#记录限制时怎么说)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
