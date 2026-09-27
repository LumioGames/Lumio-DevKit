# Tick 顺序

Tick（逻辑帧）把输入、系统和已提交结果排成确定顺序。Sample 能直接核对的是挖矿业务的局部顺序；完整宿主内部阶段以当前 SDK 的公开文档为准，不从一个系统的属性名推导更多阶段。

## 玩家挖一下矿时发生什么

下面按 `origin/main` 的声明和实现串起一帧到后续结算：

1. GAS 先对 `MineAbility.Input.TargetHex` 执行 `CanActivate`，确认目标是仍有储量的 `VeinEntity` 且在可接受距离内。拒绝时不进入 `Execute`，也不应扣费。
2. `MineAbility.Execute` 在当前世界读取 `AttributeComponent` 与 `VeinReserveComponent`。普通一击立即减少体力和剩余次数；最后一击只调用 `OrderFinalDig`，把地形事务和 `PendingDigComponent` 记录排入等待结果。
3. 服务器注册的 `SampleMiningSystem` 标记为 `[System(TickPhase.ProcessorPlan)]`，其 `Execute(World world)` 调用 `world.Single<SampleMiningComponent>().Advance()`。这个系统在生成的 `Gameplay/generated/server/Lumio.Sample.Gameplay.Registry.g.cs` 中以 `SampleMiningSystem` 登记。
4. `SampleMiningComponent.Advance()` 先接上当前 `HostVoxelWorldAdapter`，调用 `Settle` 消费 `DrainResults().Results`；只有结果表示格子确实发布时，才按 `PendingDigComponent.Serial` 顺序结算体力、矿脉和掉落。修订冲突或拒绝是一次业务拒绝，不应假装成功。
5. 同一个 `Advance()` 随后设置绑定策略并继续扫描 Section。`TryLocate` 找不到位置时返回“这一侧未知”，不是“没有绑定”；预测客户端没有服务器扫描系统。

因此，调用“已排入”与业务已经完成是两件事：最终地形、实体和属性要等结果进入结算阶段后再观察。`WorldEntity` 的声明把示例世界 Tick 率标成 `TickRateHz = 20`，不要在玩法代码中另造一套时钟。

## 系统能做什么

- 在 `EcsSystem.Execute(World world)` 中读取已有组件，推进本系统的业务状态，并调用项目已经接好的协调端口。
- 把待结算信息放进实体组件（Sample 使用带 `[Persist]` 的 `PendingDigComponent`），让跨帧等待可被存档和恢复。
- 通过明确的 `TickPhase` 登记顺序，让生成的注册表记录系统；一个系统只做它声明的那一段工作。

## 系统不能做什么

- 不能从 Native/体素回调里直接改 ECS 世界，或在玩法里手写第二个提交循环；应等待 `HostVoxelWorldAdapter` 的结果并在 `Settle` 处理。
- 不能把缺块、未知绑定、事务已排入或文件存在当成已应用；也不能把操作拒绝升级成整世界失败。
- 不能在客户端系统里伪造服务器储量、库存或掉落。客户端预测只走 GAS 提供的路径，权威结果回来后再修正。
- 不能根据一个 Sample 系统宣称完整引擎帧序列已被验证；本页只覆盖 Sample 的挖矿接缝，完整运行仍需 Host 和实际日志。

有关体素提交和“接收意图不等于落地”的边界见 [体素写入](../../lumio-voxel/references/mutations.md)；双端编译规则见 [项目布局](../../lumio-development/references/project-layout.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
