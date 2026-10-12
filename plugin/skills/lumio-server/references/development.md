# 开发服务端玩法并验证结果

服务端把玩家输入变成最终游戏结果，再让客户端看到更新。

## 用聊天走一遍

1. 玩家 A 发送聊天请求。
2. `ChatComponent.Server.cs` 处理请求，产生聊天通知。
3. 玩家 B 的客户端收到通知并显示。
4. 核对服务器记录和接收方状态，确认消息真正送达。

声明和两端文件如何组织，见 [同步与 RPC](../../lumio-gameplay/references/sync-and-rpc.md)；技能、费用、冷却和预测统一见 [GAS 技能](../../lumio-gameplay/references/gas-abilities.md)。

## 编译与装载

在 Sample 根目录执行 [README](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/README.md) 的命令（Apache-2.0）：

```sh
dotnet build LumioSample.slnx
```

默认构建服务端玩法，排除 `*.Client.cs`；模板 `Server/Config/Startup/server.json` 指向 `Gameplay/bin/Debug/net10.0/Lumio.Sample.Gameplay.dll`。修改为 Release 前先构建对应输出。客户端使用单独目录，见 [客户端搭建](../../lumio-client/references/setup.md)。

玩法放在 `Gameplay/`，生成文件放在 `Gameplay/generated/`。声明与生成注册表的步骤见 [代码生成](../../lumio-gameplay/references/code-generation.md)。

## 配表与一帧顺序

`config_dir` 使用 `Server/Config/Tables/` 的导出结果。改源表后重新导出并核对内容指纹，操作见 [配表](../../lumio-config/SKILL.md)。

Sample 世界帧率声明在 [Gameplay/EntityTypes/WorldEntity.cs](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/EntityTypes/WorldEntity.cs)，是 `TickRateHz = 20`，生成注册表据此报告帧率。不要在宿主或玩法中另起时钟推进世界。挖掘、体素提交与掉落的先后关系见 [每帧顺序](../../lumio-gameplay/references/tick.md)。

## 保存与重启验证

按 [搭建](setup.md) 运行完整导览，分别检查聊天、移动、挖掘和拾取。第十四步会停止 DS，在同一存储目录上重启，再由 `SampleRestoreVerifyScenario` 核对恢复后的世界。

检查 `DS_CHECKPOINT`、`DS_STOPPED` 与恢复结果；仅有检查点文件不足以说明格子、实体和库存都恢复正确。失败时保留原存储目录，按 [排障](diagnostics.md) 找首次错误。

源码入口：[聊天服务端](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Components/Chat/ChatComponent.Server.cs)、[恢复验证场景](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Client/Bots/SampleRestoreVerifyScenario.cs)、[导览判定](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Tools/tour-steps.mjs)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
