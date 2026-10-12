# 同步与 RPC

同步让指定客户端收到持续变化的字段；RPC（Remote Procedure Call，远程过程调用）传递一次操作或事件。

## 用聊天走一遍

1. `Gameplay/Components/Chat/ChatComponent.cs` 把 `SendMessage(string text)` 声明为 `[ServerRpc("chat.input")]`，把 `OnChatMessage(string line)` 声明为 `[ClientRpc(Scope.Room)]`。
2. `Gameplay/Components/Chat/ChatComponent.Client.cs` 的 `Say(string text)` 调用 `SendMessage`，由生成代码发送到服务器。
3. `Gameplay/Components/Chat/ChatComponent.Server.cs` 实现 `SendMessage`：拒绝空文本，以及“实体 ID + 文本”合成后超过 512 个 UTF-8 字节的聊天行，保存 `LastMessageText`、`LastMessageTick`，再调用 `OnChatMessage(line)`。
4. 服务器把这一行发给房间接收者；客户端的 `OnChatMessage` 把它写入日志。新进房间的人不会通过这次 RPC 自动补收历史聊天；两个保存字段本身使用 `Scope.None`，也不上网。

共享声明摘自 [`Gameplay/Components/Chat/ChatComponent.cs`](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Components/Chat/ChatComponent.cs)，提交 `f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb`，许可证 Apache-2.0：

```csharp
    [ServerRpc("chat.input")]
    public partial void SendMessage(string text);
```

## 字段该同步给谁

`Scope`（接收范围）决定读者；`Authority`（允许从哪一侧发起字段写入）决定写者；`[Persist]` 决定是否存档。三者不能混为一谈。

| 声明 | 玩家看到的结果 | Sample 位置 |
| --- | --- | --- |
| `Scope.Aoi` | AOI（Area of Interest，视野范围）内的观察者接收。对于箱子和矿脉，这取决于玩家是否订阅它所在的 Section（地图分块）。 | `Gameplay/Components/Box/BoxComponent.cs` 的 `Name`、`Locked`；`Gameplay/Components/Vein/VeinReserveComponent.cs` 的 `Remaining`。 |
| `Scope.Room` | 房间观察者接收，无需因字段本身而限定到箱子所在分块。 | `Gameplay/Components/Ore/OrePileComponent.cs` 的 `Amount`；`Gameplay/Components/Identity/IdentityComponent.cs` 的 `Name`、`ColorHue`。 |
| `Scope.Claim` | 只有 `claimBy` 指定的成员接收。服务器把连接的 `NetEntityId`（网络实体身份）加入箱子的 `Openers` 时，该连接收到当前完整库存与 `granted`（授予查看资格）；移除时收到 `revoked`（撤销查看资格）。 | `Gameplay/Components/Box/BoxComponent.cs` 的 `Inventory` 与 `Openers`；`Gameplay/Components/Box/BoxComponent.Server.cs` 的 `Open`、`Close`。 |
| `Scope.None` | 不上网。可以存服务器临时状态，也可以配合 `[Persist]` 保存服务器状态。 | 箱子的 `Openers` 不保存；`Gameplay/Components/Mining/PendingDigComponent.cs` 的等待记录保存。 |

`IdentityComponent.Name` 为 `Scope.Room, Authority.Owner`，`ColorHue` 为 `Scope.Room, Authority.Server`：两者接收范围相同，写入来源不同。`Scope.Owner`（只给所属连接）的业务字段用例在示例中尚未提供，不要根据 `Authority.Owner` 推断名字只对自己可见。

在玩家眼里，靠近矿脉并订阅相应分块后能获得该处实体与显示字段，离开订阅范围后不再持续收到它的 AOI 更新。进入箱子所在区域能看到名字与锁，不代表已经获准看库存；开箱者列表本身一直留在服务器。客户端界面应随订阅变化和查看资格撤销移除旧内容，不能继续把缓存当作最新值。

## 双端文件怎么拆

共享 `.cs` 放双方需要的声明和逻辑；同名 `partial`（一个类型分到多个文件）实现按端放置。Sample 的 `Directory.Build.targets` 在服务器编译排除 `**/*.Client.cs`，在客户端编译排除 `**/*.Server.cs`。`ChatComponent` 因此由服务器实现入站方法、客户端实现显示方法，另一侧调用的发送代码由生成器补齐。

修改 RPC 后按 [代码生成](code-generation.md) 构建两端，检查 `Gameplay/generated/server/Lumio.Sample.Gameplay.Registry.g.cs` 仍把 `ChatComponent.SendMessage` 映射为 `chat.input`。客户端输入到达服务器后仍要检查权限、目标和内容，不把“能收到调用”当作“允许执行”。

需要新加入者得到当前值时使用 `Sync<T>`（同步单值）或 `SyncList<T>`（同步列表）；一次聊天通知使用 RPC。若对端看不到变化，依次检查字段范围、Section 订阅或 `Openers` 成员、两端构建版本；聊天再查 `chat.input` 映射、字节长度与两端日志。宿主连接见 [客户端技能](../../lumio-client/SKILL.md)，服务端运行与日志见 [服务器技能](../../lumio-server/SKILL.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）