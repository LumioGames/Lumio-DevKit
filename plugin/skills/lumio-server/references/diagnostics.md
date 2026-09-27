# 服务器日志与排障

先找本次运行最早的失败，再判断是配置、启动、连接、玩法还是保存出了问题。

## 找到本次日志

启动器打印 `EVIDENCE_PATH`，默认位于 `.run/launch-…/`。以下名称来自 [Tools/launcher.mjs](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Tools/launcher.mjs)，均相对本次运行目录：

| 文件或目录 | 用途 |
| --- | --- |
| `verification.json` | 十四步判定与总体结果。 |
| `lumio-ds.check-config.log` | 配置检查结果。 |
| `lumio-ds.log` / `lumio-ds.boot-2.log` | 第一次启动与恢复启动的控制台输出。 |
| `ds-boot-1/` / `ds-boot-2/` | 两次运行的服务器日志。 |
| `server.boot-1.json` / `server.boot-2.json` | 启动器实际生成的配置。 |
| `bot-1/result.ndjson` / `bot-verify/result.ndjson` | 挖矿场景与恢复场景的操作和判定记录。 |

单独运行 DS 时，日志由 `logging.dir` 决定；Sample 模板解析到 `Server/Diagnostics/Logs/`。分享日志前去掉密码、票据和完整用户数据。

## 按阶段定位

| 现象 | 先检查 | 下一步 |
| --- | --- | --- |
| 直接报缺环境 | 指明的 Engine 路径、平台或 Docker | 按 [搭建](setup.md) 补前置条件。 |
| 配置检查失败 | 配置检查日志和实际配置 | 修正字段、路径或配额，确认没有复用旧生成配置。 |
| 进程在，但没有 `DS_READY` | `DS_FATAL` 首个原因、程序集、底图与配表 | 按失败阶段修复；端口监听不代表完成加载。 |
| Ready 后进不了房 | 当前房间票、`allocation`、验票公钥、关闭原因 | 用 [错误码](../../lumio-development/references/diagnostics.md#按症状查错误码) 定位。 |
| 挖矿失败 | `mining_stage`、`mining_applied`、`mining_refused` 与 Bot 结果 | 对齐同一次操作，分清排入、实际应用与拒绝。 |
| 第十四步失败 | 两次 DS 日志、同一存储目录与恢复 Bot 结果 | 保留存档，检查地图、实体和矿石数。 |

`DS_DRAINING` 表示开始停止接收新工作；`DS_CHECKPOINT` 表示输出检查点；正常结束还应查看 `DS_STOPPED` 与退出码。恢复失败时不要拼接不同检查点，或删除原件后把新空世界当作恢复成功。

## 交回诊断

记录版本、去敏命令、退出码、失败步骤、首个错误和相关日志片段。操作拒绝、服务器内部故障、客户端断线与存档损坏分别处理。

更多入口：[客户端日志](../../lumio-client/references/diagnostics.md)、[体素写入](../../lumio-voxel/references/mutations.md)、[通用诊断](../../lumio-development/references/diagnostics.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
