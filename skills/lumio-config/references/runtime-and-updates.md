# 运行时读取与配置更新

## 运行时前置

CLI 能导出不代表机器上已安装 Lumio SDK。先按 [开始开发](../../lumio-development/references/getting-started.md) 取得兼容的已交付包源，按 [项目结构](../../lumio-development/references/project-layout.md) 接入 Reader。可用能力与环境阻塞见 [能力说明](../../lumio-development/references/capabilities.md)，问题报告见 [诊断](../../lumio-development/references/diagnostics.md)。

本页核对日期为 2026-09-14，公开消费样例为 `LumioSample b236d2e`，导出器为 `LumioConfig f0dba85`。SDK API 示例是原创用法；用法编译与文件装载不等于真实 DS/客户端已接通。

## 从文件到 typed Reader

在 `Lumio.GameRuntime.Config` 中，实际装载入口是：

```csharp
LumioConfigLoader.Load(
    string exportDirectory,
    ConfigTarget target,
    IReadOnlyList<string>? requiredTables = null,
    ConfigLayer layer = ConfigLayer.Server,
    Func<ConfigTarget, IReadOnlyList<ConfigSnapshotTable>, ITypedTableSet>?
        typedTableFactory = null);
```

传入包含根 `manifest.json` 的导出根，而非 `server/` 子目录。`ConfigTarget.Server`、`.Client`、`.Voxel` 选择目标投影；`ConfigLayer` 是来源层级，不能代替目标端。返回 `LumioConfigLoadResult`，检查 `IsSuccess`，并保留 `ErrorCode`、`ErrorMessage`、`RevisionId` 和指纹。

Loader 读取和校验文件；`typedTableFactory` 用它给出的 `ConfigSnapshotTable/Row/Cell` 构建生成的表类型。工厂当前收到的是规范单元格文本（`CanonicalText`），仍需要按 Reader 的字段类型转换一次；不能把它描述为已自动生成所有表绑定。省略工厂可能装载成功而没有 `TypedTables`。

## 一个完整的 movement 绑定示例

先用 [导出命令](edit-and-export.md) 生成 `server/MovementTable.cs` 并将其纳入项目编译。以下服务端示例只绑定 movement；新增表应在装载边界扩展绑定，游戏帧内继续使用生成的 Reader。

```csharp
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using Lumio.Config.Generated.Server;
using Lumio.GameRuntime.Config;

public sealed class MovementConfig : ITypedTableSet
{
    public MovementTable Movement { get; }

    private MovementConfig(MovementTable movement) => Movement = movement;

    public bool TryGetTable<TTable>(out TTable table)
    {
        if (typeof(TTable) == typeof(MovementTable))
        {
            table = (TTable)(object)Movement;
            return true;
        }
        table = default!;
        return false;
    }

    public static MovementTable Load(string exportRoot)
    {
        LumioConfigLoadResult loaded = LumioConfigLoader.Load(
            exportRoot, ConfigTarget.Server,
            requiredTables: new[] { "movement" }, typedTableFactory: Bind);
        if (!loaded.IsSuccess)
            throw new InvalidOperationException(
                $"{loaded.ErrorCode}: {loaded.ErrorMessage}");
        if (loaded.TypedTables is not MovementConfig typed)
            throw new InvalidOperationException("movement Reader 未绑定。");
        return typed.Movement;
    }

    private static ITypedTableSet Bind(
        ConfigTarget target, IReadOnlyList<ConfigSnapshotTable> tables)
    {
        if (target != ConfigTarget.Server)
            throw new NotSupportedException("此工厂只绑定服务器投影。");
        ConfigSnapshotTable source = tables.Single(t => t.TableId == "movement");
        var rows = new List<MovementRow>();
        foreach (ConfigSnapshotRow row in source.Rows)
        {
            var cells = new Dictionary<string, string>(StringComparer.Ordinal);
            foreach (ConfigSnapshotCell cell in row.Cells)
                cells.Add(cell.Column, cell.CanonicalText);
            rows.Add(new MovementRow(
                uint.Parse(Required(cells, "id"), CultureInfo.InvariantCulture),
                Required(cells, "name"),
                Finite(cells, "step_meters"),
                Finite(cells, "sweep_radius_meters")));
        }
        return new MovementConfig(new MovementTable(rows));
    }

    private static string Required(Dictionary<string, string> cells, string name)
    {
        if (!cells.TryGetValue(name, out string? text))
            throw new FormatException($"movement 缺少必填列 {name}。");
        return text;
    }

    private static double Finite(Dictionary<string, string> cells, string name)
    {
        double value = double.Parse(Required(cells, name), CultureInfo.InvariantCulture);
        if (!double.IsFinite(value))
            throw new FormatException($"movement.{name} 必须是有限数值。");
        return value;
    }
}
```

这个工厂不读文件，也不放默认数值。格式或绑定异常会向调用者暴露；不能假设所有异常都已包装成 `LumioConfigLoadResult`，应在启动/装载边界保留诊断并拒绝这份配置。

启动时装载一次，随后通过生成的接口读取：

```csharp
MovementTable movement = MovementConfig.Load("config");
// 70001 是此公开示例的稳定行号，实际游戏用自己的已登记配置身份。
if (!movement.TryGet(70001u, out MovementRow row))
    throw new InvalidOperationException("movement 缺少游戏所需的行。");
double stepMeters = row.StepMeters;
```

生成的 `MovementTable` 同时提供 `Count` 与按 `Id` 升序的 `Rows`；`TryGet` 未命中返回 `false`，不能继续使用 default row 的零值。用行号选择规则，不依赖“第一行就是默认行”。上面的 `Load` 放在项目启动/配置接入处，不放进每帧 Processor。

公开 Sample 的 `SampleTables` 展示三表消费位置，但它会缓存首次装载结果；`SampleTypedTables` 中还存在解析失败回零的辅助方法。可参考绑定结构，新的必填数据处理应像上例明确报错，不能把这些回零写法当必需约定。

## 数值更新与 Schema 更新

| 变更 | 需要更新 | 怎样证明生效 |
| --- | --- | --- |
| 只改行值 | 新 JSON 与配套 manifests | Reader 字节不变；新进程读出新值/Revision |
| 改列类型、列名、必填或可见性 | JSON、Reader、工厂/消费代码与程序集 | 重新生成/编译；目标端读到相应类型；隐藏列不存在 |
| 改引用或删行 | 源、registry/墓碑、引用消费方 | 校验通过；缺行分支有明确结果，无编号复用 |

Sample 的可靠开发流程是：在新目录导出 → 校验 → 设置 `LUMIO_CONFIG_DIR` → 重启相应进程 → 核对运行时读值。`server.json` 的 `config_dir` 是 Host 配置，Sample 的环境变量覆盖也要一致。`ResetCache`、`Use` 与 `OverrideMining` 是测试辅助，不是生产热更新协议。

## 需要运行中切换时

已有 Host 接入配置快照时，Runtime 提供 `ConfigActivationSlot.Stage(snapshot)`、`ConfigActivator.ActivateAtBarrier(tickId)` 和 `ConfigActivationSlot.AcquireForTick(tickId)`。`LumioConfigLoadResult.CreateSnapshot(snapshotId, schemaEpoch)` 可从成功装载结果创建快照；身份参数由项目的配置生命周期提供，不能用内容 hash 强转代替。

这组接口要由 Host 在 owner thread 的 Tick 屏障协调。后台文件监听器可以产生候选输入，不能直接改当前帧的活动配置。取得 `ConfigSnapshotLease` 后，在本帧通过 `TryGetTable<TTable>` 读取一致快照并及时释放。不要跨更新继续缓存从旧 lease 取出的表值来假装已经切换。

`ActivateAtBarrier` 的线程检查不等于游戏已经把它接到了正确 Tick 相。更不能因为存在 `LoadAndActivate` 等便捷入口就宣称支持自动热更新或自动生产发布。没有现成 Host 接线时，先采用重启更新；运行中切换作为单独接入任务验证。

## 验证与错误定位

- CLI 层：校验、导出与 Reader 再生成通过；S/C/V 行列符合预期。
- 文件装载层：在独立进程分别加载旧产物与新产物，用 `TryGet` 读出旧值/新值，核对 Revision；缺少必需表或错误指纹时拒绝装载。
- 游戏层：记录真实 Host 实际读取的导出根与 Revision，再观察移动距离或挖掘费用变化。编译通过不证明这一层。
- 在线切换层：旧 Tick lease 保持旧值，新 Tick 取得新值；失败候选不替换活动快照。只对实际执行过的场景报告通过。

常见 Loader 诊断包括 `MANIFEST_NOT_FOUND`、`REQUIRED_TABLE_MISSING`、`REVISION_FINGERPRINT_MISMATCH`、`TABLE_CONTENT_FINGERPRINT_MISMATCH` 和 `PROJECTION_PUBLIC_ROOT_MIXED`。先保留实际错误，查导出根、完整性、目标端与匹配版本，再重新生成正确产物。不要关闭指纹检查或替换成硬编码数值。

公开资料：[Sample 首次装载与缓存](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/src/Lumio.Sample.Gameplay/Config/SampleTables.cs)、[Sample 工厂](https://github.com/LumioGames/LumioSample/blob/b236d2e12206dd1f5b12a9958810d92c2f49f13c/src/Lumio.Sample.Gameplay/Config/SampleTypedTables.cs)、[生成 Reader 合同](https://github.com/LumioGames/LumioConfig/blob/f0dba85efc2a3935fa0ab18c643d49523166ff4e/docs/reference/csharp-reader.md)。
