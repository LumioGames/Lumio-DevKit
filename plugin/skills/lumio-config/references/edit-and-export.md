# 修改数值、校验与生成

以下命令在 LumioConfig checkout 根执行；把 `python3` 绑定到 Python 3.11 以上（Windows 可使用 `py -3.11`）。示例核对基于 `origin/main@dd127edd87a00764b2b3ffb210df9f4b8d44d70a`；本轮未在 handbook 工作区执行 LumioConfig CLI。

```bash
python3 --version
python3 tools/lumio_config.py validate
python3 tools/lumio_config.py format --check
python3 tools/lumio_config.py registry verify
python3 tools/lumio_config.py query schema movement
python3 tools/lumio_config.py query row movement default
```

`format --check` 不写源；不带 `--check` 的 `format` 会规范化源文件。保留命令退出码与错误正文；`validate --json` 可输出结构化错误。不要只检查控制台中是否出现某个“成功”单词。

## 一个可运行的数值修改

在项目工作分支上把下面内容保存为 `movement.patch.json`：

```json
{
  "table": "movement",
  "ops": [
    {
      "op": "update",
      "name": "default",
      "set": { "step_meters": 1.5 }
    }
  ]
}
```

这个例子把公开示例 `default` 行的移动步长调为 1.5 米；实际任务使用用户选择的值。先输出修改前产物，再验证并应用补丁：

```bash
python3 tools/lumio_config.py export --out build/before --csharp-out build/readers-before
python3 tools/lumio_config.py patch validate movement.patch.json
python3 tools/lumio_config.py preview movement.patch.json
python3 tools/lumio_config.py patch apply movement.patch.json --reason "调整移动步长"
python3 tools/lumio_config.py validate
python3 tools/lumio_config.py format --check
python3 tools/lumio_config.py export --out build/after --csharp-out build/readers-after
```

任一步返回非零退出码就停止，不继续应用或替换产物。对 `step_meters=-1` 等边界输入，应分别执行 `patch validate` 与 `preview`；补丁预检不能替代完整校验。

`preview` 在隔离目录计算补丁影响，不修改源；它的模拟器结果可能是 `unavailable`，不能因此声称游戏表现已测过。`patch apply` 写入表源但不自动 Git commit。应用前的预检不授权修改生产环境。

源更新成功后，对照 `server/movement.json` 和 `client/movement.json` 的新行值，并比较两次生成的 Reader。此补丁验证中 S/C 的 `step_meters` 都变为 1.5，15 个生成 Reader 文件保持逐字节相同。Schema 类型、名称、必填或可见性改变时，Reader 改变属于预期，需要重编消费程序集。

## 导出根与产物

正式生成命令按游戏项目约定选择输出路径，例如：

```bash
python3 tools/lumio_config.py export \
  --out build/game-config \
  --csharp-out generated/csharp \
  --csharp-namespace Lumio.Config.Generated
```

导出包含根 `manifest.json`、各端 `manifest.json` 与 `<table>.json`、`origins.json`。每端 Reader 写入 `server/`、`client/`、`voxel/`；默认命名空间分别为 `Lumio.Config.Generated.Server`、`.Client`、`.Voxel`。某端没有可见列时不会为该端生成这张表的 Reader。

manifest 中的 `revisionId`、内容指纹、包裹指纹、底稿指纹描述不同身份，不能互相替换；同一份数据与工具应可重复导出。游戏运行期使用完整、匹配的产物集合。不要仅替换一个表 JSON 而留下旧 manifest，否则指纹检查会拒绝装载。

导出到新目录有助于发现不应再存在的旧文件。校验结束后再按项目交付方式替换消费产物，避免游戏读取导出一半的目录。

## 在 Sample 中消费

Sample 的服务器导出根是 `Server/Config/Tables/`，客户端导出根是 `Client/Config/Tables/`；`Gameplay/Tables/` 只保存源表、Schema 和 registry。旧的根目录 `config/`、`maps/` 和 `server.json` 不再是当前布局。

数值改动：把完整的新导出作为本地待测试的配置根，设置 `LUMIO_CONFIG_DIR` 指向它，再启动新的 Sample 进程。不要靠重编玩法把数字带进去，也不要把环境变量指向 `server/` 子目录。

Schema 改动：除导出数据外，还要生成并接入新的 Reader。Sample 有现成同步入口；下例以 Sample 与 LumioConfig 同级 checkout 为例：

```bash
export LUMIO_CONFIG_ROOT="../LumioConfig"
node Tools/sync-config-readers.mjs
node Tools/sync-config-readers.mjs --check
```

这个脚本只同步 Sample 的 `movement`、`mining`、`attributes` 三表在 S/C 两端的六个 Reader，**不会**同步 JSON 数据，也不会自动处理新加的表。新的游戏表须更新自己项目的 Reader 编译输入与运行时绑定。

## 校验拒绝怎么处理

错误落在 Schema/单元格时修改源并重新生成。引用或 registry 错误要修复真实身份关系，不能删除墓碑或跳过校验。客户端列隔离错误需要修订可见性与发包内容。CLI 只在旧 Python 写表时报 `write_text(..., newline=...)` 不支持时，先核对解释器版本；本指南要求 3.11 以上。

完成记录应包含源改动、执行命令、退出码、新 Revision、端投影检查与实际消费验证。CLI 成功只证明配表管线，后续步骤见 [运行时读取与更新](runtime-and-updates.md)。

公开资料：[CLI](https://github.com/LumioGames/LumioConfig/blob/dd127edd87a00764b2b3ffb210df9f4b8d44d70a/docs/reference/cli.md)、[Sample Reader 同步脚本](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Tools/sync-config-readers.mjs)、[Sample 配置根](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Gameplay/Tables/README.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
