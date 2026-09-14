# 开发客户端输入与表现

## 一条聊天输入的最小场景

前置：已取得含 `Lumio.Client.Bot` 公共类型的开发程序集，游戏的生成注册表声明 `chat.input`，并构建客户端侧玩法 DLL。Bot 程序集是否在分发包中需实际核对；这里不假设存在可安装的独立 Bot NuGet 包。

场景契约是 `IBotScenario.RequiredCapabilities`、`Setup`、`Step`、`Assert`；继承 `BotScenario` 可以只覆盖需要的方法。以下是原创示例，放入自己的场景类库；类型名供 `--scenario-name Guide.ChatOnce` 使用。它等待输入可用，只提交一次，拒绝后保留原因且不重试：

```csharp
using System.Collections.Generic;
using Lumio.Client.Bot;

namespace Guide;

public sealed class ChatOnce : BotScenario
{
    private bool attempted;
    private string rejection = "";

    public override IReadOnlyList<string> RequiredCapabilities =>
        new[] { "chat.input" };

    public override BotStepResult Step(in BotDriverContext context)
    {
        if (!context.World.HasSelf || !context.World.InputEnabled)
            return BotStepResult.Continue;

        if (!attempted)
        {
            attempted = true;
            if (!context.Vocabulary.TryGet(BotInputKind.ChatInput, out var term)
                || !term.Available)
            {
                rejection = "chat input unavailable";
                return BotStepResult.Complete;
            }

            var result = context.Issue(BotIssuedCommand.Chat(in term, "hello"));
            if (!result.Accepted)
            {
                rejection = result.Reason;
                return BotStepResult.Complete;
            }
        }

        return context.Uplinks > 0
            ? BotStepResult.Complete : BotStepResult.Continue;
    }

    public override void Assert(in BotDriverContext context, BotAssertionSink sink)
    {
        sink.That(attempted, "input_was_ready");
        sink.That(rejection.Length == 0, "input_rejected: " + rejection);
        sink.That(context.Uplinks > 0, "observed_uplink");
    }
}
```

该例于 2026-09-14 在临时 net10.0 项目中，使用 .NET SDK 10.0.400 和现有 Bot 开发程序集编译通过（0 警告、0 错误）；未执行真实宿主或网络验证。使用其他发布时仍以随包 XML API 文档核对签名。它只断言真正上行；要证明聊天被应用，再在第二个独立账号客户端的 `World.ChatWindow` 中检查这条消息，并对齐服务器证据。不能把 `Issue.Accepted` 当作广播已完成。

`BotDriverContext.World` 是只读观察面：`HasSelf`、`InputEnabled`、`Self`、实体数量和 `ChatWindow`。通过 `Vocabulary` 获取组件/成员/参数类型，再用 `Issue` 提交命令，不在场景中直接推进世界或修改副本。`TryGet` 找到的项也可能不可用，仍须检查 `Available` 与 `BlockedReason`。

## 从场景走到游戏客户端

1. 把输入绑定到本客户端拥有的 Self；未准入或初始数据未提交时禁用交互。
2. 普通业务 RPC 使用生成的客户端调用口；Bot 使用词表和 `BotIssuedCommand`。`DispatchServerRpc` 是服务端入站分发口，不能拿来发送客户端命令。
3. 成功应用权威结果后再刷新 UI。聊天窗口、插值数据和本地特效由表现层持有；不能反写为服务器真值。
4. 能力预测走 Runtime/GAS 的已提供路径。不要用按钮点击后直接修改 `LogicTransform` 来绕过尚未接通的上行。

公开示例可以阅读 [客户端聊天包装](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/src/Lumio.Sample.Gameplay/Components/Chat/ChatComponent.Client.cs) 和 [Local 火花实体声明](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/src/Lumio.Sample.Gameplay/EntityTypes/MiningSparkEntity.Client.cs)。声明和包装存在只证明相应代码可读，仍需真实输入、权威应用和表现证据。

## 当前限制

- Bot 的 `Activate` 词表项仍被标记不可用，命令出口会拒绝。移动/挖掘 Ability 类存在，不代表 Bot 能驱动它们。
- `FillSamples` 的原始输入通道尚未完整接到生产上行；可用场景通过 `context.Issue` 发送已支持命令。
- Sample 当前玩家绑定使用记录型物理端口；移动 Sweep 异常被捕获后表现为不移动，缺少明确错误。两者都是现状限制，不能作为接入真实碰撞或错误处理的模板。
- 浏览器最小消费宿主尚不能证明完整游戏客户端已发布；Unity、HybridCLR 与可视化游戏编辑器不是当前可依赖的安装步骤。

准备扩展前查 [能力与限制](../../lumio-development/references/capabilities.md)，选择已接通路径；无法表达所需输入时，提交缺失能力说明和最小复现，不写无声替身。
