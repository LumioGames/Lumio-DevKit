# v0.0.2 手册整理核对记录

核对日期：2026-09-27。本文记录本轮手册整理的证据边界；文档静态检查、Sample 构建和十四步运行分别记账，不能相互替代。目标插件版本为 0.3.0，不是引擎版本。

## 核对基线

| 来源 | 核对基线 | 证据 |
| --- | --- | --- |
| LumioSample | origin/main · f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb | git -C <LumioSample> rev-parse origin/main 返回该 SHA。不得从脏工作区读取。 |
| LumioEngineRelease | v0.0.2 · peeled commit 9e57979049fe727e02992ad48116ce1324a42277 | git ls-remote https://github.com/LumioGames/LumioEngineRelease.git refs/tags/v0.0.2 refs/tags/v0.0.2^{} 返回 tag object 8be501dc69c4be4678b147f43939a6ecd0f77420 与该 peeled commit；发布物 manifest.json 的 version 为 0.0.2。 |
| LumioConfig（仅在手册仍引用时核对） | origin/main · dd127edd87a00764b2b3ffb210df9f4b8d44d70a | git -C <LumioConfig> rev-parse origin/main。 |
| LumioGame（仅在手册仍引用时核对） | origin/main · 6a053af4618fff341af8cf0345e233054be4d0e8 | git -C <LumioGame> rev-parse origin/main。 |
| 插件 | plugin.json 目标版本 0.3.0 | 改动后读 plugin/plugin.json，再以 tools/sync-manifests.py --check 对适配文件作一致性核对。本轮开始时旧值为 0.2.0，不能把旧值当作完成证据。 |

发布物 v0.0.2 的 SDK 包为 sdk/Lumio.Engine.SDK.0.0.2.nupkg。从发布 tag 读取其目录可见 content/docs/public-api.md、content/docs/error-codes.md、content/sdk-version.json 和 content/wire/；错误码页声明覆盖 257/257 个公共码。核对命令如下，输出只保留文件名和版本，不把包解压进项目：

~~~sh
curl -LfsS https://raw.githubusercontent.com/LumioGames/LumioEngineRelease/v0.0.2/manifest.json
curl -LfsS https://raw.githubusercontent.com/LumioGames/LumioEngineRelease/v0.0.2/sdk/Lumio.Engine.SDK.0.0.2.nupkg -o <tmp>/Lumio.Engine.SDK.0.0.2.nupkg
unzip -l <tmp>/Lumio.Engine.SDK.0.0.2.nupkg | grep -E 'content/(docs/(public-api|error-codes)\.md|sdk-version\.json)$'
unzip -p <tmp>/Lumio.Engine.SDK.0.0.2.nupkg content/sdk-version.json | head
~~~

因此 diagnostics 页可以直接以该包的 content/docs/error-codes.md 为完整表来源，正文只挑按症状需要的常见码；“没有随附参考”这一上游缺口不成立。manifest.json 列出的运行平台是 win-x64 和 linux-x64；其它平台若未取得对应发布物，仍须记作 BLOCKED_ENV。

## Sample 路径、类名和命令核对表

以下结果来自 origin/main 的只读 git cat-file / git grep，不是本机 Sample 工作区。Engine 是 gitlink，使用 git ls-tree 核对。

| 手册引用 | 核对命令 | 只读结果 |
| --- | --- | --- |
| Gameplay/EntityTypes/BoxEntity.cs | git -C <LumioSample> cat-file -e origin/main:Gameplay/EntityTypes/BoxEntity.cs | PRESENT |
| Gameplay/Components/Box/BoxComponent.cs | git -C <LumioSample> cat-file -e origin/main:Gameplay/Components/Box/BoxComponent.cs | PRESENT |
| Gameplay/Abilities/MineAbility.cs、.Server.cs、.Client.cs | 对三个路径分别执行 cat-file -e | 均 PRESENT |
| Gameplay/Abilities/PickupAbility.cs、.Server.cs、Gameplay/Effects/PickupOreEffect.cs | 对三个路径分别执行 cat-file -e | 均 PRESENT |
| Gameplay/Config/SampleConfigBinding.cs、SampleTypedTables.cs、SampleTables.cs | 对三个路径分别执行 cat-file -e | 均 PRESENT；配置运行时示例直接取自这些文件 |
| Gameplay/Abilities/MoveAbility.cs、Gameplay/SampleMiningComponent.Client.cs、.Server.cs | 对三个路径分别执行 cat-file -e | 均 PRESENT；查询、物理扫掠和挖穿提交示例均可回指 |
| Server/Assets/Maps/、Server/Config/Startup/server.json | 对路径执行 cat-file -e | 均 PRESENT |
| Tools/launcher.mjs、Tools/tour-steps.mjs、Tools/update-engine.mjs | 对三个路径分别执行 cat-file -e | 均 PRESENT；update-engine.mjs 的用法是 node Tools/update-engine.mjs <version> |
| Client/Assets/Blocks/、Tools/check-block-assets.mjs | 对路径执行 cat-file -e | 均 PRESENT |
| .github/workflows/tour.yml、Client/Bots/SampleMiningScenario.cs、Client/Bots/SampleRestoreVerifyScenario.cs | 对三个路径分别执行 cat-file -e | 均 PRESENT；十四步由 Tools/launcher.mjs 驱动，CI 工作流文件不是根目录 tour.yml |
| Engine 子模块 | git -C <LumioSample> ls-tree origin/main Engine | 160000 commit 9e57979049fe727e02992ad48116ce1324a42277 Engine，与 v0.0.2 peeled commit 一致 |
| 已改名的旧路径 src/Lumio.Sample.Gameplay、maps、server.json、integration/launcher.mjs | 对每项执行 git cat-file -e origin/main:<旧路径> | 均 OLD_ABSENT；不要把缺失旧路径误报为 Sample 缺文件 |
| HostEntry | git -C <LumioSample> grep -n -F 'Lumio.Server.HostEntry.HostEntry, Lumio.Server.HostEntry' origin/main -- Server/Config；再查 LumioHostEntry | server.json、server.sample.json、server.acceptance.json 均出现 Lumio.Server.HostEntry.HostEntry 与 LumioHostEntry |
| BlockId 宽度 | git -C <LumioSample> grep -n -E 'uint blockId|uint.*BlockId' origin/main -- Gameplay Server | MineAbility.ClassifyPredictedDig(..., uint blockId, ...) 等消费面出现 uint；字段最终含义仍以 SDK v0.0.2 公共参考为准 |

有三个容易误判的静态结果：ISampleVoxelBinding 只在 Sample 的退役说明/测试中留下历史文字，生产绑定入口不是它；RecordingAbilityPhysicsPort 在测试夹具中仍可出现，不能据全仓 grep 断言“仓库没有”；catch (Exception) 在客户端旁观宿主等其它代码中可能存在，验收时必须限定 Gameplay/Abilities/MoveAbility*。这些结果只能证明引用没有把已退役的消费入口写成当前 API，不能证明宿主真实运行。

## 本仓三项检查

下列命令已在完成文档和 plugin/plugin.json 改动后从仓根执行；结果只说明本仓插件检查，不替代 Sample、DS、Bot 或浏览器运行。

| 检查 | 命令 | 结果 |
| --- | --- | --- |
| 生成适配文件一致性 | python3 tools/sync-manifests.py --check | PASS（exit 0）：Host adapters match portable manifest |
| 包内 schema、技能元数据和相对链接 | python3 tools/validate.py | PASS（exit 0）：skills=7, issues=0 |
| 安装器/校验器回归 | python3 -m unittest discover -s tests -v | PASS（exit 0）：Ran 20 tests in 0.064s，OK；它不证明 Sample、DS、Bot 或浏览器运行。 |

validate.py 只检查插件包边界、frontmatter 和 Markdown 文件链接，不能证明链接页内容准确、API 签名存在或客户端真的加载技能。sync-manifests.py --check 只证明适配文件由 plugin/plugin.json 生成，不能证明安装器或宿主 UI 可用。

## 文档内容验收

逐项复核以下要求，未找到对应证据时保持未完成：

1. getting-started 使用 git clone --recursive 或 git submodule update --init 获取 Engine/，升级只写 node Tools/update-engine.mjs <版本>，不再把 -p:LumioLocalFeed= 当作当前模板必经步骤。
2. 全手册使用新路径 Gameplay/、Server/Assets/Maps/、Server/Config/Startup/server.json、Tools/launcher.mjs；旧路径只可出现在迁移提示或历史说明。
3. lumio-server/setup 使用 Lumio.Server.HostEntry.HostEntry / LumioHostEntry；体素页按 SDK v0.0.2 说明 BlockId 为 uint，不把退役的 ISampleVoxelBinding.TryBind、Recording 物理端口或 MoveAbility 宽泛捕获写成当前接线。
4. 美术页引用 WebGL2、方块资产契约、Client/Assets/Blocks/ 和 Tools/check-block-assets.mjs，并区分文件检查与浏览器画面复验。
5. 客户端页写清 git、.NET SDK、Node、Docker 等前置；十四步真实结果只能由 step=NN、DS 日志、Bot 生命周期日志、result.ndjson 和第 14 步同存储重启证据给出。
6. 新增 lumio-gameplay，入口保持短小，至少有 entities-and-components、sync-and-rpc、gas-abilities、tick、code-generation 五篇 reference；每个 Sample API 例子能由上表的 git grep / cat-file 回指。
7. diagnostics 按症状列四列（关闭原因/错误码、含义、处理方式等）；DS 关闭原因来自 Engine/web/ds-close-codes.mjs，体素/持久化码来自 SDK 包内 content/docs/error-codes.md，Host/Sample 私有码已明确标注。
8. README 新增只含链接的“按顺序学”：入门 → 概念 → 教程（十四步）→ 操作 → 参考 → 排障；不要复制 reference 正文。
9. 每篇 reference 末尾只保留一行统一证据边界：核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）。能力不存在、未接线、缺运行环境和本次未验证四种情况要分别写。
10. README 当前阶段与本文件基线一致；正文不出现私有仓路径、绝对本机路径、内部单号或凭据；只改 DevKit，不改 Sample、Engine 或其它引擎仓。

可用下面的静态筛查找漏项，但它不是内容正确性的充分证据；排除了本记录和明确的迁移提示，剩余命中才需要修正文案：

~~~sh
rg -n 'src/Lumio\.Sample\.Gameplay|(^|[^A-Za-z])maps/|integration/launcher\.mjs|ISampleVoxelBinding\.TryBind|RecordingAbilityPhysicsPort|catch \(Exception\)' plugin/skills README.md --glob '*.md' --glob '!plugin/skills/lumio-config/references/edit-and-export.md'
rg --files-without-match '核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0\.0\.2' plugin/skills -g '*.md'
~~~

## Sample 构建和十四步运行

这两项不能以接口存在、静态路径或仓内单元测试替代。为避免读取脏工作区，使用新的临时目录和递归子模块，并显式检出上面的 origin/main SHA：

~~~sh
git clone --recursive https://github.com/LumioGames/LumioSample.git <tmp>/LumioSample
git -C <tmp>/LumioSample checkout f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb
git -C <tmp>/LumioSample submodule update --init --depth 1 Engine
cd <tmp>/LumioSample
dotnet build LumioSample.slnx
~~~

本轮在新的递归临时 clone 中完成上述干净目录构建：checkout 为 f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb，Engine gitlink 为 9e57979049fe727e02992ad48116ce1324a42277，manifest version=0.0.2；`dotnet build LumioSample.slnx` exit 0、0 errors、2 warnings（当前 macOS RID 没有 SDK native asset，managed compile 不受影响）。构建 PASS 只覆盖编译，不替代 DS/Bot/浏览器运行。

需要 Docker 和匹配发布物时，十四步命令为：

~~~sh
dotnet build Gameplay/Lumio.Sample.Gameplay.csproj -p:LumioEcsSide=client
dotnet build Client/Bots/Lumio.Sample.Bots.csproj
node Tools/launcher.mjs --bots 2 --stagger-ms 250 \
  --scenario-dll Client/Bots/bin/Debug/net10.0/Lumio.Sample.Bots.dll
~~~

客户端 Gameplay 构建 exit 0、1 warning；Bot 默认构建在 macOS host exit 1，首个错误为 `SAMPLE_BOTS_CLIENT_BOT_MISSING`（Engine v0.0.2 仅随 win-x64/linux-x64 Bot.Host；当前 host 为 osx-x64）。以 `-p:NETCoreSdkRuntimeIdentifier=linux-x64` 可完成 Bot managed compile，但 launcher 仍按本机 RID 选择 Engine 运行物，因此不改变本机运行结论。Docker `docker info` 可用（29.5.2）。十四步 launcher 本轮记为 `BLOCKED_ENV`，未进入 step=01..14；真正通过必须同时保存：

- step=01 到 step=14 的逐步状态；任一步 BLOCKED_ENV（exit 2）都不是通过；
- 第 04 步 Bot 日志中的 Active … established，不能用 DS 进程启动替代进房；
- 第 05–13 步的 DS 日志、导览 Bot 生命周期日志和非空未截断的 result.ndjson；
- 第 14 步在同一存储上停 DS、重启并让同一账号由 SampleRestoreVerifyScenario 复核地图缺口和矿石数；
- 两轮独立目录的世界断言与哈希对账摘要。

## 上游缺口和未验证项

- SDK v0.0.2 随附公开 API、错误码和 wire 参考，已在上面的 nupkg 目录核对；不应再把“没有随附参考”写成事实。
- 发布 manifest 只列 win-x64 / linux-x64；未取得相应宿主或在其它平台运行时，应报告 BLOCKED_ENV，不得拿接口或其它平台 DLL 代替。
- 干净 Sample build 已 PASS；客户端 Gameplay 编译已 PASS；Docker 可用但 Platform/DS/Bot 十四步因 macOS 无 v0.0.2 osx-x64 发布物而为 BLOCKED_ENV，未执行真实浏览器画面、跨进程存档恢复和 Windows/Linux 矩阵。静态示例、仓内测试和适配器检查不能替代它们。
- 当前本地 Sample checkout 可能是脏的或未初始化 Engine/；它不是验收基线。只接受上表的 origin/main 和 v0.0.2 release 证据。
