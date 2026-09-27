# 运行时读取与配置更新

配置绑定把导出的表装进一个世界，让玩法读取已经检查过的数值。

以修改挖矿体力消耗为例：

1. 修改 `Gameplay/Tables/` 中的表源，重新导出服务器和客户端的数据。
2. 启动新进程时，装载器先检查目标端、必需表和指纹，再创建 Reader（带类型的表读取入口）。
3. 世界取得一份配置快照（这次装载后固定的数据集合），`MineAbility` 从中读取消耗；游戏不在每次挖矿时重新解析文件。

## 运行时前置

先按 [环境与第一步](../../lumio-development/references/getting-started.md) 初始化 `Engine/`，再按 [编辑与导出](edit-and-export.md) 更新数据和 Reader。服务器导出在 `Server/Config/Tables/`，客户端导出在 `Client/Config/Tables/`。两者都是含 `manifest.json` 的端导出根，文件装载时不能继续下钻到其中的 `server/` 或 `client/` 子目录。构建还会复制文件或嵌入浏览器程序集，更新时要检查实际消费位置。

## 从文件到 Reader

下面两段逐字摘自 [`Gameplay/Config/SampleConfigBinding.cs`](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Config/SampleConfigBinding.cs) 的 `Load`，核对提交 `f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb`，许可证 Apache-2.0；只去掉外层缩进。

```csharp
var entry = new SampleConfigBinding();
var result = LumioConfigLoader.Load(SampleTables.ResolveDirectory(directory), SampleConfigProjection.Target,
    requiredTables: entry.RequiredTables, typedTableFactory: entry.CreateTypedTables);
if (!result.IsSuccess) throw new InvalidOperationException(result.ErrorMessage);
```

`SampleTables.ResolveDirectory` 依次选择显式目录、`LUMIO_CONFIG_DIR` 环境变量、程序集旁含 `manifest.json` 的 `config/` 目录。找不到就报错。装载失败时保留 `ErrorMessage`，先查目录、端和必需表，不能用空配置继续运行。

```csharp
var module = ConfigModule.Create();
if (!module.Stage(result.CreateSnapshot(new ConfigSnapshotId(1))).Staged || !module.ActivateAtBarrier(default).Activated)
    throw new InvalidOperationException("Sample config activation failed.");
return new WorldConfigBinding(module, GeneratedRegistry.Instance, entry);
```

这里先准备快照，再在屏障（世界切换配置的安全时点）激活，最后返回世界绑定。`Gameplay/Config/SampleTypedTables.cs` 的 `Create` 构造 `mining`、`movement`、`attributes`、`map` 四张表的 Reader；`TryGetTable<TTable>` 把它们交给 `SampleConfigBinding.Project`，投影为玩法使用的 `ISampleConfig`。`SampleConfigBinding.For(world)` 从当前世界读取它，数值属于世界配置。

## 数值更新与 Schema 更新

| 变更 | 需要更新 | 怎样检查 |
| --- | --- | --- |
| 只改行值 | JSON 与配套清单，以及使用它们的文件副本或浏览器程序集 | 比较前后行值；Reader 通常不变；刷新消费产物后核对新进程读取的新值。 |
| 改列类型、列名、必填或可见性 | JSON、Reader、工厂与消费程序集 | 重新生成和编译；检查目标端类型与隐藏列。 |
| 改引用或删行 | 源、registry（永久行号记录）、墓碑与引用消费方 | 校验通过；删除编号不复用，缺行有明确处理。 |

开发时按“导出 → 校验 → 更新实际消费产物 → 重新启动或加载 → 核对游戏行为”执行：

- 直接读外部文件的服务器：`Server/Config/Startup/server.json` 的 `config_dir` 选择服务器配置根；进程使用 `LUMIO_CONFIG_DIR` 时也要指向正确的端。刷新这份完整导出后重启。
- 使用程序集旁 `config/` 的进程：`Gameplay/Lumio.Sample.Gameplay.csproj` 会在构建时复制对应端的配置文件。重新构建以刷新副本，再重启；只改仓库里的导出目录不保证旧构建输出同步变化。
- 浏览器 Spectator：`Client/UI/Spectator/Directory.Build.props` 用 `EmbeddedResource` 把客户端清单和表嵌入程序集。只改数值也要按 [浏览器构建步骤](../../lumio-client/references/setup.md) 重新构建和发布，再重新加载页面；重启服务器不能更新浏览器的嵌入数据。

移动距离或挖矿消耗没有变化时，先确认实际启动的程序、发布版本以及它使用的文件副本或嵌入数据。

## 运行中切换

Sample 展示了启动时 `Load`、准备快照、激活并绑定世界；完整的在线配置更新流程在示例中尚未提供。不要把启动代码当作文件监听回调直接放进游戏帧中。需要在线更新时，先查发布物的 `Lumio.GameRuntime.Config.xml`，由宿主协调世界的切换时点、失败处理和旧快照使用者；参考入口见 [公开 API](../../lumio-development/references/getting-started.md#查公开参考)。

## 错误定位

先分别检查导出、装载和游戏消费：导出失败查源表与 Schema（列类型和约束）；装载失败保存错误正文、目标端与清单；进程启动后再观察真实移动距离、挖矿费用或其他消费结果。不要跳过指纹检查，也不要用硬编码数值覆盖缺表错误。

公开源码：[目录选择](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Config/SampleTables.cs)、[Reader 工厂](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Config/SampleTypedTables.cs)；相关操作见 [编辑与导出](edit-and-export.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
