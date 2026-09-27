# 客户端输入、同步与表现

客户端只提交输入、消费复制快照并绘制表现；服务器仍是权威业务。共享玩法的声明放在 `Gameplay/`，端特有实现分别放 `.Server.cs` 和 `.Client.cs`。

## 从生成接口发送输入

1. 客户端读取本端输入并调用生成的客户端 RPC/命令入口。
2. 服务器在 `*.Server.cs` 中做权限、距离、资源和 GAS admission。
3. 服务器提交结果，Runtime 生成复制差分。
4. 客户端应用自己的 Replica，再由 UI 或 Local Entity 表现。

Sample 的聊天入口可读 `Gameplay/Components/Chat/ChatComponent.cs`、`ChatComponent.Client.cs` 与 `ChatComponent.Server.cs`。Bot 场景应使用生成的客户端入口，不要调用服务端 `DispatchServerRpc` 或自拼 wire。

## 看见什么才算送达

编译成功只证明客户端程序集可加载；收到 `Welcome` 只证明连接/准入。要证明一条聊天或实体更新已送达，必须同时观察：发送方入站记录、服务器权威应用、复制消息、接收方的客户端状态或 UI。一个客户端看不到另一个玩家可能是 AOI 范围之外，先核对 Scope 与实体位置。

## 预测和回滚

地形修改和碰撞预测由 GAS 统一管理。客户端画面可以先出现预测洞或碰撞变化，待权威结果回来后 GAS 保留、纠正或回放未确认记录；业务库存、掉落和奖励不另造一套客户端预测。预测数据缺失时保持等待，不把未知地形画成空气。

## 验证

- 使用两个独立 launch 票运行客户端，记录连接代次和目标 Engine 发布物。
- 发送一条聊天、移动一次、触发一次挖矿；逐段对齐 DS、Bot、Replica 和 UI 日志。
- 让目标离开 AOI，再进入 AOI，确认实体出现/离开符合复制语义。
- 复现一次被拒绝输入，确认只有这次操作失败而连接保持 Active。

未执行的真实浏览器、Native 物理或冷恢复步骤写“本次未验证”。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
