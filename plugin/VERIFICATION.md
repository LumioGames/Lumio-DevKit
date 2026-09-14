# 首版验证记录

核对日期：2026-09-14。DevKit `0.1.0` 是指引与技能包，不是引擎版本；以下结果不能互相替代。

## 使用说明的阅读基线

| 公开来源 | 本次核对提交 |
| --- | --- |
| [LumioSample](https://github.com/LumioGames/LumioSample) | `b236d2e12206dd1f5b12a9958810d92c2f49f13c` |
| [LumioConfig](https://github.com/LumioGames/LumioConfig) | `f0dba85efc2a3935fa0ab18c643d49523166ff4e` |
| [LumioGame](https://github.com/LumioGames/LumioGame) | `79a50ab2f7585e714f1e9b171cd34675df88f28f` |

还对照了引擎当前公共 API 签名与宿主命令实现，用原创说明描述使用面。私有实现未包含在本插件中，外部操作指南不要求读取私有源码。

## 实际运行

- 官方 Agent Plugins 1.0.0 manifest schema 与仓内路径/链接校验：`PASS: skills=6, issues=0`。六份 SKILL 另经 Agent Skills 快速校验，均通过；未把这项检查当作宿主 UI 安装验证。
- 配表工具在独立 checkout 中使用 Python 3.11 实际完成校验、格式检查、registry/查询、补丁预检/预演/应用与导出。数值 `1.25 → 1.5` 同步进入 S/C 导出；15 个 Reader 文件不变。同源重复导出得到 23 个 JSON 和 15 个 Reader 的相同字节；S-only 列从客户端数据与 Reader 移除、服务器保留。
- 四个原创配置/体素示例类在独立 net10.0 项目引用已有程序集编译，0 warnings、0 errors；真实 Loader 读取旧/新值，验证缺行和不存在导出根的失败。体素部分只编译，不执行 Native 查询。`patch validate` 对低于 minimum 的输入不足以发现所有问题，实际 `preview` 以 `RANGE_OVERFLOW` 拒绝，指引保留了这一区别。

- 维护检查器先用无校验实现运行负例：8 项中 7 项失败；补齐后 8 项通过。覆盖坏链接、包外路径、越界软链、缺技能入口、名称不匹配和 schema 拒绝。
- 从 Sample 上述提交建立隔离快照，运行 `node --test integration/verify-evidence.mjs`：17 passed、0 skipped、退出 0。它验证证据处理工具和固定夹具，不是真实 Platform/DS/Bot 十四步。
- 客户端指引的原创 `ChatOnce` 代码从 Markdown 提取，在独立 net10.0 类库中引用已有 Bot/Input/Replica/Ecs 程序集编译：.NET SDK 10.0.400，0 warnings、0 errors。未建立网络连接，不能作为消息交付证明。
- 美术交接示例 JSON 已解析检查；未生成美术图片、运行渲染器或验证统一资产导入器。

## 本次确认的失败与限制

1. 公共 NuGet `lumio.engine.sdk` 包索引返回 HTTP 404。未把 SDK 公共发布当作已完成前提。
2. 隔离 Sample 快照与本机缓存 SDK 0.1.0 组合，restore 成功、build 失败：`NETSDK1022`，三个生成的配置 Reader 被重复计入 Compile。MSBuild 求值确认同一文件分别由默认 glob 与模板显式 Include 加入；缓存包仅有 SDK targets，未包含模板预期的 props。
3. 该次缓存 nupkg 的 SHA-256 为 `0486c8fda30b08158ce7f41a2175319babbd5f9f6043afb74d6dd6e2635759d6`。此结果只约束这组产物，不推断所有名为 0.1.0 的包都相同。没有关闭默认编译检查或修改源仓来消除失败。
4. 未执行真实双端联调、Native 体素场景、跨进程存档恢复、Windows/Linux 发行矩阵或宿主插件 UI 安装。纯配置/文档检查不代表这些链路可用。

具体步骤和受影响用法见 [入门](skills/lumio-development/references/getting-started.md)、[客户端](skills/lumio-client/SKILL.md)、[服务器](skills/lumio-server/SKILL.md)、[体素](skills/lumio-voxel/SKILL.md)、[配置表](skills/lumio-config/SKILL.md) 和 [美术](skills/lumio-art/SKILL.md)。

## 示例编译的二进制边界

配置/体素代码验证使用已有开发程序集，未重新构建源仓；因此不能证明这些文件与本次阅读的源码提交一一对应，也不替代 SDK 分发包验证。实际引用文件 SHA-256：

| 程序集 | SHA-256 |
| --- | --- |
| Config | `5bb74713fe7d5de1a7073202c666fe9f893e8e2132475e3b6254d4949e35d32d` |
| Coordination | `7855f0ddaa515ea78a7b938c027ecf7d9c6b27af514fca411a4356cc98f36653` |
| Ecs | `46f6b7840aa695c4d011b47b7f4ddd82fe1275159433b81298db3694eaeb8b57` |
| Primitives | `4a5408d6d99c61d14f64369154043c861583415e4f3026cabfd0dd106e87c0dc` |

这些程序集没有打入 DevKit；表格用于说明本次编译证据用了什么。

## 0.2.0 安装分发验证（2026-09-14）

仓库公开名称改为 `LumioGames/Lumio-DevKit`；插件与 marketplace 标识保持 `lumio-devkit`。插件本体移入 `plugin/`，技能内容保留，根目录只负责开发与分发。

- `plugins` CLI 1.3.4 本地 `discover`：发现一个插件、六个 skills。
- `claude plugin validate .` 与 `claude plugin validate plugin`：分别验证 marketplace 和插件适配。
- 独立 `CLAUDE_CONFIG_DIR` 中执行 marketplace add、plugin install、plugin list：安装 `lumio-devkit@lumio-devkit` 0.2.0 成功，enabled=true。未改用户实际 Claude 配置，未执行 Agent 会话。
- 手动安装在独立 data-dir 下分别连接模拟全局与项目 skill 目录；两处各六个 symlink 均能读取 SKILL，已安装 payload 的全部相对链接校验通过。
- 安装器与校验器合计 19 项回归通过；覆盖重复安装、更新保留旧包、同名目录/外来链接冲突、包内软链拒绝、路径重叠、dry-run、被修改的已安装包与退役 skill 清理。
- Codex 适配 manifest 校验通过；未在用户实际 Codex 中激活插件。CLI 可发现和适配格式通过，不替代所有客户端的运行验收。
