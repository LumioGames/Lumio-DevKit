# 能力入口与当前证据范围

核对日期为 **2026-09-27**；精确签名以实际使用的 Engine v0.0.2 XML 为准。接口、生成物和真实运行是三种不同证据。

## 世界里只有两种东西

- 静态、不动、没有服务器逻辑的地形是体素。
- 会动或需要服务器逻辑的角色、矿脉、掉落物是实体。
- 只在客户端显示的火花、提示等是 Local Entity。
- 固定占格但有库存的箱子：占格是体素，库存和开关逻辑是实体，两者靠稀疏引用关联。
- 技能、冷却、属性、效果和预测都由实体上的 GAS 组件承载；Sample 没有 Gameplay Tags 声明，标签能力以 Engine v0.0.2 的公开 XML/API 为准。

## 找入口

| 需求 | 公开入口 | 证据边界 |
| --- | --- | --- |
| 实体、组件和本地实体 | `Gameplay/EntityTypes/**`、`Gameplay/Components/**`、ECS XML | Sample 有声明和生成输出；创建、复制和表现仍需 Host 运行证据 |
| 同步与 RPC | `.Server.cs`/`.Client.cs`、生成的 Sync/Registry | 字段的 Scope 由 Runtime 解释；代码存在不等于客户端已收到 |
| 技能与预测 | `Gameplay/Abilities/**`、`Gameplay/Effects/**`、GAS XML | `MineAbility` 的地形预测与 `PickupAbility` 的权威效果有真实声明；回滚是否接通要看运行结果 |
| Tick 与系统 | `Gameplay/SampleMiningSystem.Server.cs`、Simulation XML | 系统顺序以发布物 Tick 合同为准；单元测试不证明跨进程时序 |
| 体素读写和查询 | `lumio-voxel` skill、Engine XML | `BlockId` 是 `uint`；Pending/Unavailable/Unresolved 不能当空气 |
| DS 与存档 | `Server/Config/Startup/server.json`、`Tools/launcher.mjs` | 需要同一版本的 DS、HostEntry、Runtime、Native 和存储目录 |
| 方块资产 | `Client/Assets/Blocks/`、`Tools/check-block-assets.mjs` | 资产契约和检查器可静态核对；实际 WebGL2 画面仍需运行验证 |
| 配表 | LumioConfig CLI 与 `Server/Config/Tables`/`Client/Config/Tables` | 导出和 Reader 成功不等于 DS 已激活该快照 |

### 四种限制措辞

- **能力不存在**：Engine v0.0.2 没有该公开类型或命令。
- **尚未接线**：Sample 有声明，但 Host/消费者没有提供运行输入。
- **缺运行环境**：缺 Docker、Platform、Engine 产物或准入票。
- **本次未验证**：没有执行对应命令或场景。

不要用 `Recording`、`Fake` 或“有一个接口”推断生产能力；追到实际构造、注入和日志。完整验证命令见 [验证记录](../../../VERIFICATION.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
