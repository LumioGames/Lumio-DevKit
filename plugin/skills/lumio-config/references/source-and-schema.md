# 表源、Schema 与可见性

本文以 2026-09-14 核对的公开 `LumioConfig f0dba85` 为例。命令执行见 [编辑与导出](edit-and-export.md)，运行期读取见 [读取与更新](runtime-and-updates.md)。

## 文件关系

| 路径 | 作者维护什么 |
| --- | --- |
| `schemas/<table>.json` | 列名、类型、稳定 `ordinal`、必填、范围、默认值、引用、可见性 |
| `tables/<table>.txt` | 当前权威行数据，pipe-table 文本 |
| `registry/` | 名字与永久行号、编号域、删除墓碑 |
| `layers/{engine,platform,server,product,environment}/` | 按层覆盖已有行的值 |
| 导出目录与 Reader 目录 | 工具输出；按项目分发约定复制或重建 |

先运行 `query schema <table>` 和 `query row <table> <name-or-id>`，避免只看列名猜数值单位。Editor、表格软件或 CSV 都不能成为绕过权威文本源的第二套数据。

## 修改 Schema 要确认的东西

每列需要唯一整数 `ordinal`；调整 JSON 数组顺序不能改变列身份。常用类型包括 `bool`、`i32`、`i64`、`u32`、`u64`、`f32`、`f64`、`string`、`enum`、`ref`。

例如一个公开移动配置列使用以下结构：

```json
{
  "name": "step_meters",
  "ordinal": 2,
  "type": "f64",
  "required": true,
  "minimum": 0,
  "visibility": "CS"
}
```

这是列片段，不是独立完整 Schema。`step_meters` 映射到 Reader 的 `StepMeters`，`f64` 映射为 `double`。`required:false` 的值类型生成可空值；`enum` 生成字符串，`ref` 生成 `uint`，不要自行替换成另一套枚举或对象关系。

本版本 `movement` 的导出端为 S/C，`step_meters` 与 `sweep_radius_meters` 都可见。修改一列前同时考虑：消费方是否要读、客户端是否应知道、引用目标在同一端是否存在、单位和边界能否由校验器检查。

## 文本单元格与单位

源文件包括 `table:`、`schema:`、列头、分隔线和数据行。字符串中的管道符写成 `\|`，字面反斜线写成 `\\`。

| 作者意图 | 表达 |
| --- | --- |
| 空字符串 | `""` |
| 显式空值 | `null`，仍受必填约束 |
| 使用 Schema 默认值 | `@default` |
| 未提供字段 | 与显式空字符串/空值不同；是否允许由 Schema 决定 |

不要用字符串 `"0"`、空格或空单元格替代这些含义。当前工具会规范化文本并拒绝无效转义、非法数值等输入；以结构化校验错误中的表/行/列为定位依据。

`unit:"seconds"` 的源数值会按 `repository.yaml` 的 `tickRate` 转成帧整数；`unit:"percent"` 会转成千分比整数。`movement.step_meters` 没有这种单位转换声明。改帧率或单位可能影响多表导出，不应只比较一张表。

## S / C / V 与发包

`visibility` 是 `S`（Server）、`C`（Client）、`V`（Voxel）的非空组合；未填写默认 `S`。导出器只把可见列放到对应端的 JSON 和 C#。

- 想让客户端显示图标或名称：确认相关列含 `C`。
- 掉落概率、隐藏关卡内容等服务器信息：按业务需要只放 S，不把它加入公共 UI 配置。
- 需要 Voxel 消费的材质数据：使用项目与 SDK 已定义的列结构和 V 投影，不把玩法脚本装进该投影。

验证时同时检查 `client/<table>.json` 的 `rows` 实际字段，以及 `client/<Table>Table.cs` 的属性。还要检查真正发出的客户端包；把整个导出根（连同 server/voxel）一起打包，会绕过列投影的目的。根 manifest 与端 manifest 要保持装载器需要的相对路径，不能通过手改 manifest 来伪造隔离。

跨端引用必须在消费端可解析。客户端隐藏的目标表不能因为服务器能找到就算客户端引用有效；以导出器的引用/可见性校验结果为准。

## 行身份、覆盖与新表

行的永久 `id` 用于稳定引用，`name` 用于可读编辑。名字补丁更新或创建行时不填写 `id`；创建由工具发号，改名用 `rename` 操作，删除记录墓碑。不要用当前数组索引代替存档或网络中的行身份。

增加完整新表需要同时完成 Schema、文本表、项目编号域/registry 接入、端可见性、导出与消费方 Reader 绑定。以项目已配置的编号域为准，不从某个示例中复制一段永久编号来占用。没有可用域就报告缺少配置，不造新的全局分配规则。

覆盖层按 `engine → platform → server → product → environment` 合并，只覆盖源表已有行。改了 `tables/` 仍看不到新值时，先查导出的 `origins.json` 与覆盖层；运行时的 Session/User 数据不是这个 CLI 的第六张作者表。

公开资料：[源格式](https://github.com/LumioGames/LumioConfig/blob/f0dba85efc2a3935fa0ab18c643d49523166ff4e/docs/reference/source-format.md)、[movement Schema](https://github.com/LumioGames/LumioConfig/blob/f0dba85efc2a3935fa0ab18c643d49523166ff4e/schemas/movement.json)、[Reader 类型映射](https://github.com/LumioGames/LumioConfig/blob/f0dba85efc2a3935fa0ab18c643d49523166ff4e/docs/reference/csharp-reader.md)。
