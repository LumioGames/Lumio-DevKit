# 客户端输入、同步与表现

客户端发送玩家操作，接收服务器结果，并把结果显示给玩家。

## 用聊天看完整流程

1. Bot 等待客户端副本知道“我是谁”。
2. 从宿主提供的输入词表找到聊天入口，提交一句话。
3. 服务器处理聊天并通知接收者。
4. 客户端显示通知；输入已接受和别人实际看见消息是两件事。

声明、两端文件与 RPC（发给另一端的调用）见 [同步与 RPC](../../lumio-gameplay/references/sync-and-rpc.md)。视野范围和字段同步规则也集中在该页。

## 沿 Sample 写 Bot

[Client/Bots/SampleMiningScenario.cs](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Client/Bots/SampleMiningScenario.cs) 的 `SampleMiningScenario` 是运行场景；[SampleMiningPlan.cs](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Client/Bots/SampleMiningPlan.cs) 根据当前可见世界决定下一步移动、挖掘或拾取。

以下原文摘自 `Client/Bots/SampleMiningScenario.cs`，提交 `f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb`，Apache-2.0：

```csharp
        if (world.HasSelf && !_chatAccepted
            && context.Vocabulary.TryGet(BotInputKind.ChatInput, out BotInputTerm chatTerm)
            && chatTerm.Available)
        {
            BotIssueResult chat = context.Issue(BotIssuedCommand.Chat(chatTerm, "sample tour: hello from the mining bot"));
            if (chat.Accepted) _chatAccepted = true;
            else _lastReject = chat.Reason;
        }
```

场景使用真实输入词表，不猜组件编号或网络字段。失败时保留 `Reason`，根据更新后的世界决定下一次操作。构建和运行见 [客户端搭建](setup.md)。

## 预测与画面

移动、技能、冷却和预测统一由 GAS（挂在实体上的技能系统）处理，见 [GAS 技能](../../lumio-gameplay/references/gas-abilities.md)。只供画面使用的火花可以是本地实体，见 [实体与组件](../../lumio-gameplay/references/entities-and-components.md)。

浏览器三维方块画面从客户端世界取数据；缺数据时显示等待状态，不能当作空气。资源替换与透明度检查见 [世界资产](../../lumio-art/references/world-assets.md)。

## 验证一次改动

先查输入是否被接受，再对照 DS 记录与接收方世界。聊天应到达接收者；挖矿应核对格子、掉落和拾取后的数值。日志入口见 [客户端排障](diagnostics.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
