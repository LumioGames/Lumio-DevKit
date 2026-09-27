# 客户端日志与排障

先判断卡在启动、准入还是玩法步骤，再对照同一次运行的服务器记录。

## 从导览查起

启动器打印的 `EVIDENCE_PATH` 是本次运行目录。文件名和判定来自 [Tools/launcher.mjs](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Tools/launcher.mjs) 与 [Tools/tour-steps.mjs](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Tools/tour-steps.mjs)。

| 记录 | 能说明什么 | 还要看什么 |
| --- | --- | --- |
| `verification.json` | 哪个步骤失败 | 对应的 DS 与 Bot 日志。 |
| `bot-1/admission-events.ndjson` | 连接与准入进度 | 是否到达 `admitted` 及后续操作结果。 |
| `bot-1/result.ndjson` | 挖矿场景的输入与判定 | 请求是否最终造成服务器状态变化。 |
| `bot-verify/result.ndjson` | 恢复验证结果 | 同一存储下的地图和矿石数。 |
| 浏览器 Console / Network | 页面加载、连接与资源错误 | 世界是否应用，画面是否出现。 |

输入已接受只说明请求进入出口；上行产生也不等于服务器已应用。使用接收方状态或对应断言确认业务结果。

## 常见现象

| 现象 | 处理 |
| --- | --- |
| Engine 或客户端程序集缺失 | 检查子模块，按 [搭建](setup.md) 构建客户端与 Bot。 |
| Bot 已启动但未准入 | 查准入日志、DS Ready 与房间票，按 [错误码](../../lumio-development/references/diagnostics.md#按症状查错误码) 处理关闭原因。 |
| 挖矿没反应 | 对照 `SampleMiningScenario` 输入结果、DS 日志与当前可见目标；离开视野不等于被挖掉。 |
| 收到首个方块区域后失败 | 启动器默认传入 `Server/Assets/Maps/bot-voxel-budget.json`；收到方块数据的房间不能关闭体素预算配置。 |
| 浏览器白屏 | 确认服务的是发布目录，检查 `_framework/`、`lumio_voxel_wasm.wasm` 和 import map（模块名到发布文件的映射表）。 |
| 只有俯视图，没有三维方块 | 在打印的页面地址后加 `?view=blocks`，检查 WebGL2 与资源请求。 |
| 方块显示紫黑格 | 查看资产警告和缺失贴图，按 [美术验收](../../lumio-art/references/integration-and-review.md) 修复。 |

## 断线与重试

保留原始关闭原因，区分正常结束、网络中断与数据应用失败。由现有宿主处理连接生命周期，新会话按宿主流程取得新票。不要直接重发旧会话中结果未知的输入，否则可能重复执行。

公开入口：[浏览器连接和画面](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Client/UI/Spectator/main.js)、[挖矿场景](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Client/Bots/SampleMiningScenario.cs)。交回时附去敏命令、版本、退出码、失败步骤与第一条错误；服务器端查 [服务器日志](../../lumio-server/references/diagnostics.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
