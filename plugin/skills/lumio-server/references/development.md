# 开发服务端玩法并验证结果

## 构建游戏的服务端侧

玩法工程保留在游戏仓的 `Gameplay/`；SDK 提供 Runtime，Engine 发布物提供 DS 与宿主。Sample 的默认构建是服务端侧，会排除 `*.Client.cs`：

```sh
dotnet build Gameplay/Lumio.Sample.Gameplay.csproj -c Release -o Gameplay/bin/Release/net10.0
```

客户端另建输出目录并选择客户端侧：

```sh
dotnet build Gameplay/Lumio.Sample.Gameplay.csproj \
  -c Release -p:LumioEcsSide=client
```

客户端构建使用 Sample 的 `net10.0-client` 隔离输出；如果明确构建浏览器副本，再传 `-p:LumioBrowserReplica=true` 并使用 `net10.0-browser` 输出。预期输出包含玩法 DLL、生成注册表和与 `Engine/manifest.json` 相同版本的 Runtime 依赖。`Server/Config/Startup/server.json` 的 `clr.registry_assembly` 指向服务端玩法 DLL；HostEntry 始终来自 Engine 发布物，不能拿游戏 DLL 冒充入口。

共享玩法的声明在 `Gameplay/Components/`、`Gameplay/EntityTypes/`、`Gameplay/Abilities/` 和 `Gameplay/Effects/`；生成结果写入 `Gameplay/generated/`，不要手改生成文件。服务器和客户端实现放在同名 `.Server.cs` / `.Client.cs`，由 `LumioEcsSide` 选择。

## 从聊天确认权威执行

公开入口可阅读 [聊天声明](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Components/Chat/ChatComponent.cs)、[服务端实现](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Components/Chat/ChatComponent.Server.cs)。用户操作通过生成的 ServerRpc 接口进入；服务端写自己的数据，再产生客户端事件。

最小人工验证：

1. 用 `node Tools/launcher.mjs` 起一个明确的测试房间，记录 `DS_READY` 的版本和内容指纹。
2. 用两个不同账号取得各自房间票，连接两个独立客户端；确认两者都 Active。
3. 客户端 A 发送一条可识别的短聊天。对齐上行、服务器处理日志与客户端 B 的已提交聊天窗口。
4. 再发送一次无效输入，确认该次操作有可定位拒绝，后续合法输入仍能执行。不要把断开整房间作为拒绝反馈。

## 配表、Tick 与世界能力

`config_dir` 指向 `Server/Config/Tables/` 的 export，而不是源表目录。启动期间会校验 manifest 身份并调用 Runtime 装载；检查 Ready 的 `contentFingerprint`，再在实际玩法读表路径确认读到了目标行和值。

调 Tick 时以世界提供的 `tickRate` 为准。Sample 的 Tick 配置来自 `Server/Config/Startup/server.json`；不要另加宿主时钟或在玩法层模拟第二个逻辑 Tick。技能、冷却、消耗和预测走 GAS；体素意图由 Runtime 在 Tick 提交阶段应用。

Sample 的 `MoveAbility`、`MineAbility` 和 `PickupAbility` 已在 `Gameplay/Abilities/`，`PickupOreEffect` 在 `Gameplay/Effects/`。挖掘最后一击由 `MineAbility.Server.cs` 暂存地形单并在结果回读后结算；客户端由 `MineAbility.Client.cs` 走 GAS 预测。`PickupAbility` 保持权威执行，`PickupOreEffect` 在结算阶段入账。未运行完整 DS/Bot 时只能报告静态代码和编译证据。

## 保存与重启验证要单独安排

正常运行的检查点会输出 `DS_CHECKPOINT` 与 generation；它证明这一组存储发布完成，不自动证明客户端状态、底图语义或冷恢复正确。`runtime+voxel` 要求同一组中具备 Runtime 和 Voxel 两半，不能只保存 ECS。

要验证保存，先确认本次任务允许停机和使用该测试目录，然后正常停止前台进程（Ctrl+C，或向选定进程发 SIGTERM），等待 `DS_STOPPED` 和退出 0。保留检查点，再按恢复测试计划启动并比较挖过的格子、实体身份与数值，而不只比较一个哈希。未执行的步骤写“未执行”。

当前 `snapshot_only` 不能证明每次已接受操作都耐久；游戏对存档的要求应依据实际发布能力，不根据配置名字作承诺。

公开阅读：[玩法目录](https://github.com/LumioGames/LumioSample/tree/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay)、[启动器](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Tools/launcher.mjs)、[挖掘技能](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Abilities/MineAbility.cs)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
