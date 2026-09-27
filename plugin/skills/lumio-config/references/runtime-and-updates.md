# 运行时读取与配置更新

## 运行时前置

CLI 能导出不代表机器上已安装 Lumio SDK。先按 [开始开发](../../lumio-development/references/getting-started.md) 取得兼容的已交付包源，按 [项目结构](../../lumio-development/references/project-layout.md) 接入 Reader。可用能力与环境阻塞见 [能力说明](../../lumio-development/references/capabilities.md)，问题报告见 [诊断](../../lumio-development/references/diagnostics.md)。

本页核对日期为 2026-09-27，公开消费样例为 `LumioSample f98322c`，导出器为 `LumioConfig origin/main@dd127edd87a00764b2b3ffb210df9f4b8d44d70a`。代码片段摘自 Sample 的配置绑定；编译与文件装载不等于真实 DS/客户端已接通。

## 从文件到 typed Reader

公开 Sample 的真实装载入口在 [`Gameplay/Config/SampleConfigBinding.cs`](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Config/SampleConfigBinding.cs)。它先构造 `SampleConfigBinding`，再把 `SampleTables.ResolveDirectory`、目标端、必需表和 `SampleTypedTables.Create` 交给 Runtime：

```csharp
var entry = new SampleConfigBinding();
var result = LumioConfigLoader.Load(SampleTables.ResolveDirectory(directory), SampleConfigProjection.Target,
    requiredTables: entry.RequiredTables, typedTableFactory: entry.CreateTypedTables);
if (!result.IsSuccess) throw new InvalidOperationException(result.ErrorMessage);
```

上面代码逐字来自 Sample 的 `SampleConfigBinding.Load`。`SampleTables.ResolveDirectory` 会依次考虑显式目录、`LUMIO_CONFIG_DIR` 和程序集旁含 `manifest.json` 的 `config/` 目录；不要把单个 `server/` 子目录当作导出根。加载成功后，Sample 创建快照、在屏障激活，再返回 `WorldConfigBinding`：

```csharp
var module = ConfigModule.Create();
if (!module.Stage(result.CreateSnapshot(new ConfigSnapshotId(1))).Staged || !module.ActivateAtBarrier(default).Activated)
    throw new InvalidOperationException("Sample config activation failed.");
return new WorldConfigBinding(module, GeneratedRegistry.Instance, entry);
```

生成的 typed Reader 由 [`Gameplay/Config/SampleTypedTables.cs`](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Config/SampleTypedTables.cs) 的 `Create` 构造；它把 `mining`、`movement`、`attributes`、`map` 四张表绑定到 `SampleTypedTables`，并通过 `TryGetTable<TTable>` 暴露给 `SampleConfigBinding.Project`。这是当前 Sample 的接线方式，不是一个可复制到所有项目的自定义 `MovementConfig` API。

如果项目没有同样的 `IGameConfigExportBinding`、`SampleConfigProjection` 或生成 Reader，记录为“示例中尚未提供”，先以实际 Engine XML 和项目生成物为准；不要照抄不存在的签名。加载失败应保留 `ErrorMessage`、目标端、导出根和版本身份，不能用默认行或空配置掩盖缺件。

## 数值更新与 Schema 更新

| 变更 | 需要更新 | 怎样证明生效 |
| --- | --- | --- |
| 只改行值 | 新 JSON 与配套 manifests | Reader 字节不变；新进程读出新值/Revision |
| 改列类型、列名、必填或可见性 | JSON、Reader、工厂/消费代码与程序集 | 重新生成/编译；目标端读到相应类型；隐藏列不存在 |
| 改引用或删行 | 源、registry/墓碑、引用消费方 | 校验通过；缺行分支有明确结果，无编号复用 |

Sample 的可靠开发流程是：在新目录导出 → 校验 → 设置 `LUMIO_CONFIG_DIR` → 重启相应进程 → 核对运行时读值。`Server/Config/Startup/server.json` 的 `config_dir` 是 Host 配置，Sample 的环境变量覆盖也要一致。`ResetCache`、`Use` 与 `OverrideMining` 是测试辅助，不是生产热更新协议。

## 需要运行中切换时

当前公开 Sample 展示的是启动时 `SampleConfigBinding.Load`、创建快照并在屏障激活，然后由 World 使用绑定结果；Sample 没有展示一套可直接复制的在线热更新 API。需要运行中切换时，先在目标 Engine v0.0.2 的公开 XML/wire 参考中核对实际类型和方法，再由 Host 在自己的 Tick 屏障协调候选配置；后台文件监听器不能直接改当前帧的活动配置。

没有 Sample 接线和真实运行证据时，采用“导出新目录 → 校验 → 重启进程 → 核对新 Revision”的流程，并把在线切换记录为“示例中尚未提供”或“本次未验证”。不要把某个未核对的 `LoadAndActivate`、快照 lease 或激活方法名写成当前模板能力。

## 验证与错误定位

- CLI 层：校验、导出与 Reader 再生成通过；S/C/V 行列符合预期。
- 文件装载层：在独立进程分别加载旧产物与新产物，用 `TryGet` 读出旧值/新值，核对 Revision；缺少必需表或错误指纹时拒绝装载。
- 游戏层：记录真实 Host 实际读取的导出根与 Revision，再观察移动距离或挖掘费用变化。编译通过不证明这一层。
- 在线切换层：旧 Tick lease 保持旧值，新 Tick 取得新值；失败候选不替换活动快照。只对实际执行过的场景报告通过。

常见 Sample/Host Loader 诊断（本轮未执行 Loader 实例复测）包括 `MANIFEST_NOT_FOUND`、`REQUIRED_TABLE_MISSING`、`REVISION_FINGERPRINT_MISMATCH`、`TABLE_CONTENT_FINGERPRINT_MISMATCH` 和 `PROJECTION_PUBLIC_ROOT_MIXED`；这些名称不等同于 SDK 公共 `content/docs/error-codes.md` 条目。先保留实际错误，查导出根、完整性、目标端与匹配版本，再重新生成正确产物。不要关闭指纹检查或替换成硬编码数值。

公开资料：[Sample 首次装载与缓存](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Config/SampleTables.cs)、[Sample 工厂](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Config/SampleTypedTables.cs)、[生成 Reader 合同](https://github.com/LumioGames/LumioConfig/blob/dd127edd87a00764b2b3ffb210df9f4b8d44d70a/docs/reference/csharp-reader.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
