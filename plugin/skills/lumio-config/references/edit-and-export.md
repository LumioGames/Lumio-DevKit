# 修改数值、校验与生成

这页把一次玩法数值修改从表源带到服务器和客户端使用的导出文件。

以调整玩家移动距离为例：

1. 在 `Gameplay/Tables/tables/movement.txt` 找到 `default` 行，用 `Gameplay/Tables/schemas/movement.json` 确认 `step_meters` 的类型和范围。
2. 修改源表后导出两端数据；服务器和客户端用于预测的移动数值必须一致。
3. 再生成 Reader（读取已装载表的 C# 类型），重新编译，并启动新进程观察移动距离。

## 准备工具

准备 Python 3.11 以上和公开 [LumioConfig](https://github.com/LumioGames/LumioConfig) 检出。把 LumioConfig 放在 Sample 同级目录，或将 `LUMIO_CONFIG_ROOT` 设置为它的仓库根；Windows 的脚本默认通过 `py -3` 启动 Python，也可用 `LUMIO_PYTHON` 选择解释器。

Sample 的源根是 `Gameplay/Tables/`，不是 LumioConfig 仓自己的演示表。CLI（命令行工具）默认处理 LumioConfig 自己的表；检查游戏表时必须用 `--root` 指向游戏源根。

## 校验源表

下面在 LumioConfig 仓根运行，以 Sample 和 LumioConfig 同级为前提。Windows 把 `python3` 替换为 `py -3`：

```sh
python3 tools/lumio_config.py validate --root ../LumioSample/Gameplay/Tables
python3 tools/lumio_config.py format --check --root ../LumioSample/Gameplay/Tables
python3 tools/lumio_config.py registry verify --root ../LumioSample/Gameplay/Tables
python3 tools/lumio_config.py query schema movement --root ../LumioSample/Gameplay/Tables
python3 tools/lumio_config.py query row movement default --root ../LumioSample/Gameplay/Tables
```

`format --check` 只检查格式；不带 `--check` 会改写源文件。`validate --json` 输出结构化错误。每一步都要检查退出码，失败时先修复相应的表、行或列。

需要按名字批量改行时，使用 CLI 的 `patch validate`、`preview`、`patch apply`；补丁格式和参数见 [公开 CLI 参考](https://github.com/LumioGames/LumioConfig/blob/dd127edd87a00764b2b3ffb210df9f4b8d44d70a/docs/reference/cli.md)。`preview` 在临时目录计算影响，不修改源；`patch apply` 写源但不自动提交 Git。Sample 中尚未提供可直接摘录的补丁文件，因此这里不另编补丁示例。

## 在 Sample 中导出

回到 Sample 仓根执行，命令摘自 [`Gameplay/Tables/README.md`](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Tables/README.md)，核对提交 `f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb`，许可证 Apache-2.0：

```sh
node Tools/sync-config-export.mjs
node Tools/sync-config-readers.mjs
node Tools/sync-config-export.mjs --check
node Tools/sync-config-readers.mjs --check
```

`sync-config-export.mjs` 在两个临时目录分别导出，比较所有产物字节，再同步到 `Client/Config/Tables/` 和 `Server/Config/Tables/`，并移除编译器已经不再输出的旧文件。`--check` 比较当前仓库产物，不覆盖它们。服务器的 `acceptance` 地图配置另导出到 `Server/Config/Profiles/acceptance/`。

`sync-config-readers.mjs` 同步 `movement`、`mining`、`attributes`、`map` 四张表在服务器和客户端的八个 Reader，写入 `Server/Config/Generated/` 与 `Client/Config/Generated/`；它本身不复制 JSON 数据。新增表还要接入游戏的 Reader 编译输入与配置绑定。

数值修改通常只改变导出 JSON，Reader 类型保持不变；改列类型、名字或可见性时，Reader 也会改变。若配置被复制到构建输出，需刷新那份副本；浏览器将表嵌入程序集，即使只改数值也必须重新构建和发布。具体步骤见 [运行时更新](runtime-and-updates.md#数值更新与-schema-更新)。不要手改生成的 JSON、Reader、manifest（描述一组导出文件的清单）或指纹。

## 两端隔离和失败定位

LumioConfig 的 `export --client-out ... --server-out ...` 把 C（客户端）数据写入客户端根，把 S（服务器）和 V（体素引擎）数据写入服务器根。Sample 的同步脚本已经使用这种方式；不要把包含服务器隐藏列的整份导出发给客户端。

| 现象 | 检查与处理 |
| --- | --- |
| 校验时报行号、引用或墓碑错误 | 修复源与 registry 的真实关系，不能重用删除行的编号。 |
| 改了源表但导出没有变化 | 检查 `--root`，再检查覆盖层和导出的 `origins.json`。 |
| Reader 检查不一致 | 用同一个 LumioConfig 版本重新生成，再检查 Schema 是否改变。 |
| 客户端拿到了服务器字段 | 检查 `visibility` 和实际发包目录；修源后重新导出。 |
| 文件已更新但游戏仍用旧数值 | 按 [运行时读取与更新](runtime-and-updates.md) 刷新消费文件或浏览器发布产物，再重新启动并核对实际数据。 |

LumioConfig 命令和生成规则依据提交 `dd127edd87a00764b2b3ffb210df9f4b8d44d70a` 的 [CLI](https://github.com/LumioGames/LumioConfig/blob/dd127edd87a00764b2b3ffb210df9f4b8d44d70a/docs/reference/cli.md) 与 [Reader 参考](https://github.com/LumioGames/LumioConfig/blob/dd127edd87a00764b2b3ffb210df9f4b8d44d70a/docs/reference/csharp-reader.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
