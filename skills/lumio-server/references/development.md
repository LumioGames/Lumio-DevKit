# 开发服务端玩法并验证结果

## 构建游戏的服务端侧

玩法工程保留在游戏仓；SDK 提供 Runtime，DS 提供进程与网络。示例的默认侧是 server，会排除 `*.Client.cs`。在通用搭建已准备好的本地 SDK feed 下，从 LumioSample 根目录执行：

```sh
dotnet build src/Lumio.Sample.Gameplay/Lumio.Sample.Gameplay.csproj \
  -c Release -p:LumioLocalFeed="$LUMIO_SDK_FEED" -o .run/server
```

预期输出 `.run/server/Lumio.Sample.Gameplay.dll` 与兼容 Runtime 依赖。将 `clr.registry_assembly` 指向此游戏 DLL，Replication/Ecs 指向相同输出集，HostEntry 则仍使用 DS 分发的入口程序集。不要从不同构建目录各挑一个“名字一样”的 DLL。`LUMIO_SDK_FEED` 只是命令示例中的路径变量。

声明写在游戏源码，生成结果由 SDK 构建步骤更新；详细 [项目布局](../../lumio-development/references/project-layout.md) 和 [能力边界](../../lumio-development/references/capabilities.md) 是共同参考。

## 从聊天确认权威执行

公开入口可阅读 [聊天声明](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/src/Lumio.Sample.Gameplay/Components/Chat/ChatComponent.cs)、[服务端实现](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/src/Lumio.Sample.Gameplay/Components/Chat/ChatComponent.Server.cs)。用户操作通过生成的 ServerRpc 接口进入；服务端写自己的数据，再产生客户端事件。

最小人工验证：

1. 起一个明确的测试房间，记录 Ready 的版本与内容指纹。
2. 用两个不同账号取得各自房间票，连接两个独立客户端；确认两者都 Active。
3. 客户端 A 发送一条可识别的短聊天。对齐上行、服务器处理日志与客户端 B 的已提交聊天窗口。
4. 再发送一次无效输入，确认该次操作有可定位拒绝，后续合法输入仍能执行。不要把断开整房间作为拒绝反馈。

Sample 的现有服务端聊天对空文本和超长内容直接返回，尚未提供上述完整拒绝反馈；现有例子不能证明这一验收项已满足。长文本还受到 UTF-8 wire 长度限制，字符数不能代替字节数。

## 配表、Tick 与世界能力

`config_dir` 指向 export，不是源表随意存放的目录。启动期间会校验 manifest 身份并调用 Runtime 装载；错误通过 `config_load_failed` 的 detail 暴露。检查 Ready 的 `contentFingerprint`，再在实际玩法读表路径确认读到了目标行和值。当前 Host 不传必需表清单，不能声称 DS 已替游戏校验全部“必需表”；装载成功也不能替代玩法消费证明。

调 Tick 时以世界提供的 `tickRate` 为准。当前 DS 要求 `1000 % tickRate == 0`，例如 50 Hz 可整除，60 Hz 会拒绝 Ready。可选 `clr.tick_rate_hz` 会影响启动世界配置；不要另加 `host.tick_hz`，也不要改宿主循环模拟另一个逻辑时钟。

Sample 有移动与挖掘声明，但当前 Bot Activate、真实物理端口和完整十四步仍有缺口。`world_profile=runtime+voxel` 只有在 Runtime 返回有效体素世界后才 Ready；若缺能力，应明确报告，不将其改为 runtime-only 后声称玩法可用。

## 保存与重启验证要单独安排

正常运行的周期检查点会输出 `DS_CHECKPOINT` 与 generation；它证明这一组存储发布完成，不自动证明客户端状态、底图语义或冷恢复正确。`runtime+voxel` 要求同一组中具备 Runtime 和 Voxel 两半，不能只保存 ECS。

要验证保存，先确认本次任务允许停机和使用该测试目录，然后正常停止前台进程（Ctrl+C，或向选定进程发 SIGTERM），等待 `DS_STOPPED` 和退出 0。强杀不是正常收尾证据。保留这一组检查点，再按明确的恢复测试计划启动并比较挖过的格子、实体身份与数值，而不只比较一个哈希。

**现状限制：**当前 `lumio-ds` 启动会自动读取 `store_path` 中可用检查点，且可能因同身份组损坏选择更旧的完整组；CLI 没有独立的“只启动、不恢复”开关。这不满足需要显式选择每次恢复的工作流。不要用循环启动、删除最新组或换空目录来伪装恢复成功；若要求禁止自动恢复，先报告宿主能力缺口。

当前 `async` / `snapshot_only` 不能证明每次已接受操作都耐久；`durable` 仅在支持的平台按文件/目录同步提供更强检查点保证。游戏对存档的要求应依据实际发布能力，不根据配置名字作承诺。
