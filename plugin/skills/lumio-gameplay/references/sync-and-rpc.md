# 同步与 RPC

同步决定某个字段由哪些客户端看到；RPC（Remote Procedure Call，远程过程调用）传递一次操作或事件。先选字段范围，再把声明和端实现拆开，最后核对生成的注册表。

## 用聊天走一遍

Sample 的聊天是一个最小的客户端到服务器再回到房间的例子：

1. `Gameplay/Components/Chat/ChatComponent.cs` 的共享声明标记 `SendMessage(string text)` 为 `[ServerRpc("chat.input")]`，并标记 `OnChatMessage(string line)` 为 `[ClientRpc(Scope.Room)]`。
2. 客户端在 `Gameplay/Components/Chat/ChatComponent.Client.cs` 调用 `Say(string text)`；这个包装记录日志后调用共享的 `SendMessage`。
3. 服务器在 `Gameplay/Components/Chat/ChatComponent.Server.cs` 实现 `SendMessage(string text)`，拒绝空文本和超过 UTF-8 限制的行，写入 `LastMessageText`、`LastMessageTick`，再调用 `OnChatMessage(line)`。
4. 生成的 `Gameplay/generated/server/Lumio.Sample.Gameplay.Registry.g.cs` 把 `ChatComponent.SendMessage` 映射为 `chat.input`。这条映射只说明操作进入服务器分发器；需要真实房间才能验证消息是否被另一客户端看到。

## 字段该同步给谁

| 声明 | 玩家看到的结果 | Sample 位置 |
| --- | --- | --- |
| `Scope.Aoi` | 持有该实体所在 Section 的观察者看到，例如箱子的 `Name`、`Locked` 和矿脉的 `Remaining`。离开视野后不再收到该 AOI（Area of Interest，视野范围）内的更新。 | `Gameplay/Components/Box/BoxComponent.cs`、`Gameplay/Components/Vein/VeinReserveComponent.cs` |
| `Scope.Room` | 房间内的观察者看到，例如 `OrePileComponent.Amount`、`IdentityComponent.Name` 与 `ColorHue`。 | `Gameplay/Components/Ore/OrePileComponent.cs`、`Gameplay/Components/Identity/IdentityComponent.cs` |
| `Scope.Claim` | 只有 `claimBy` 指定的成员看到。箱子打开时，服务器把连接的 `NetEntityId` 加入 `Openers`，Runtime 再发库存的 granted；关闭时移除并 revoked。 | `Gameplay/Components/Box/BoxComponent.cs`、`Gameplay/Components/Box/BoxComponent.Server.cs` |
| `Scope.None` | 不上网；可用于服务器账本或临时成员，例如 `Openers` 和 `PendingDigComponent` 的字段。 | `Gameplay/Components/Box/BoxComponent.cs`、`Gameplay/Components/Mining/PendingDigComponent.cs` |

`[Persist]` 与 `Scope` 是两件事：`[Persist]` 表示保存，`Scope` 表示复制范围。比如 `BoxComponent.Inventory` 两者都有，`Openers` 两者都没有；服务器重启后不会恢复谁正在打开箱子。

## 双端文件怎么拆

共享文件放声明和双方都需要的字段；同名 partial 类型的 `.Server.cs` 只放服务器代码，`.Client.cs` 只放客户端代码。Sample 的 `Directory.Build.targets` 会在服务器侧排除 `**/*.Client.cs`，在客户端侧排除 `**/*.Server.cs`。不要把服务器写入藏在共享声明里，也不要让客户端直接改权威字段。

玩家看到的 AOI 结果取决于其 Section 订阅和实体字段的 `Scope`：同一个方块实体可以让所有附近观察者看到 `Name`，只让当前 `Openers` 看到 `Inventory`，把 `Openers` 本身留在服务器。实体离开观察范围时，客户端不能把本地缓存当成最新权威值。

RPC 是一次调用，不是长期状态。若新加入的观察者必须得到当前值，应使用带正确 `Scope` 的 `Sync<T>`；若只是通知一次聊天行，使用 `ClientRpc`。服务器入站 RPC 仍需做目标、权限和内容检查。

更完整的宿主连接与客户端表现见 [lumio-client](../../lumio-client/SKILL.md)；服务器生命周期和日志见 [lumio-server](../../lumio-server/SKILL.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
