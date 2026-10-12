# 0.3.0 手册核对记录

核对日期：2026-09-27。插件版本为 **0.3.0**，引擎版本为 **v0.0.2**。以下是本次重新执行的结果；不沿用缺少原始日志的旧平台运行结论。各指引页尾说明该页的验证范围，编译与运行结果集中记在这里。

## 核对基线

| 来源 | 固定提交或版本 | 核对方法 |
| --- | --- | --- |
| LumioSample | `origin/main@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb` | fetch 后 `git rev-parse origin/main`；源代码只用 `git show`、`git grep`、`git cat-file` 读取 |
| LumioEngineRelease | `v0.0.2`，`9e57979049fe727e02992ad48116ce1324a42277` | 干净递归 clone 中的 `git submodule status`、`Engine/manifest.json`，与 Sample 的 `git ls-tree origin/main Engine` 一致 |
| LumioConfig | `origin/main@dd127edd87a00764b2b3ffb210df9f4b8d44d70a` | fetch 后读取 `origin/main` 的 CLI 和 README |
| LumioGame | `origin/main@6a053af4618fff341af8cf0345e233054be4d0e8` | fetch 后读取 `origin/main`；入门操作以 Sample 的现行子模块流程为准 |
| Lumio DevKit | `plugin/plugin.json` 中 `version=0.3.0` | 运行 `tools/sync-manifests.py` 更新生成物，再运行 `--check` |

公开 SDK 包 `Engine/sdk/Lumio.Engine.SDK.0.0.2.nupkg` 实际包含 `content/docs/public-api.md`、`content/docs/error-codes.md`、`content/docs/error-codes.json`、`content/wire/` 和 `lib/net10.0/` 下的程序集 XML。错误码页列出 257 个码，但部分说明仍笼统，见下方缺口。完整表的取得方式见 [入门：查公开参考](skills/lumio-development/references/getting-started.md#查公开参考)。

## 本仓三项检查

Windows 使用 Python 3.12.10 的隔离环境，按 `requirements-dev.txt` 安装依赖。下表中的 Python 路径相对 DevKit 仓根；WSL 使用 Ubuntu 24.04 / Python 3.12.3，在同一份手册文件上执行。

| 命令 | 环境 | 实际结果 |
| --- | --- | --- |
| `.venv/Scripts/python.exe tools/sync-manifests.py --check` | Windows | PASS，exit 0：`Host adapters match portable manifest` |
| `.venv/Scripts/python.exe tools/validate.py` | Windows | PASS，exit 0：`skills=7, issues=0` |
| `python3 -m unittest discover -s tests -v` | WSL/Linux | PASS，exit 0：20 tests，OK |
| `.venv/Scripts/python.exe -m unittest discover -s tests -v` | Windows 原生 | FAIL，exit 1：17 通过、3 errors；未修改的 `main@71a0462` 也复现相同错误 |

Windows 的三个失败是 `test_repeat_and_update_preserve_old_payload`、`test_update_removes_retired_owned_skill_link`、`test_multi_target_update_keeps_all_links_live`，均在 `owned_link` 的链接目标字符串比较后误报 `install conflict`。本 PR 未修改安装器或测试，未把这组失败算作通过。隔离环境的 Python 会额外打印 `Could not find platform independent libraries <prefix>`，上述检查仍按各自退出码和完整结果记录。

新增玩法技能另用 skill-creator 的 `quick_validate.py` 运行入口检查，开启 Python UTF-8 模式后 PASS（`Skill is valid!`）。中文文件在本机默认 GBK 模式下会使该外部检查脚本解码失败。插件检查不证明 Agent 客户端实际加载；本次未执行客户端 UI 安装验收。

## 干净 Sample 构建与发布物检查

在全新的目录执行以下命令，未从已有脏 Sample 工作区复制代码或产物：

```sh
git clone --recursive https://github.com/LumioGames/LumioSample.git LumioSample
cd LumioSample
git rev-parse HEAD
git submodule status
dotnet build LumioSample.slnx
dotnet build Gameplay/Lumio.Sample.Gameplay.csproj -p:LumioEcsSide=client
dotnet build Client/Bots/Lumio.Sample.Bots.csproj
node Engine/tools/verify-release.mjs --root Engine --rid win-x64 --version 0.0.2 --json
node Tools/check-block-assets.mjs
```

工具版本：Git 2.55.0.windows.5、.NET SDK 10.0.400、Node v24.18.0。Sample CI 配置的 Node 是 22.16.0，本次本机结果对应上述实际版本。

| 检查 | 实际结果 |
| --- | --- |
| clone 后代码身份 | Sample 和 Engine 与基线表完全一致；构建前工作区干净 |
| `dotnet build LumioSample.slnx` | PASS，exit 0，0 warnings / 0 errors；包含 Gameplay 与 Gameplay.Tests 的编译，未运行 Sample 测试 |
| 客户端 Gameplay build | PASS，exit 0，0 warnings / 0 errors |
| Bot build | PASS，exit 0，0 warnings / 0 errors |
| 发布物完整性 | PASS，exit 0；`version=0.0.2`、`rid=win-x64`、249 files；发布平台为 win-x64 / linux-x64 |
| 方块资产检查 | PASS，exit 0；24 个方块、24 份描述、22 张 128px 贴图 |

构建会重新生成 Gameplay 的客户端和服务器注册资料；这些变化只留在用于验证的 clone 中，没有修改或提交现有 Sample、引擎仓的代码。

## 十四步尝试与未验证项

Windows 原生的 `docker version` 提示命令不存在。进一步检查 WSL Ubuntu 24.04，Docker 29.8.0、.NET SDK 10.0.112、Node v22.23.2 可用，因此另建 Linux 检出尝试导览。Sample 从公开仓 clone；Engine 子模块在两次 TLS 网络失败后，改从上述已校验的公开发布物本地 Git 对象检出，同样固定在 `9e579790`，未读取或修改原有脏工作区。

| WSL 检查 | 实际结果 |
| --- | --- |
| `dotnet build LumioSample.slnx` | PASS，0 warnings / 0 errors |
| `dotnet build Gameplay/Lumio.Sample.Gameplay.csproj -p:LumioEcsSide=client` | PASS，0 warnings / 0 errors |
| `dotnet build Client/Bots/Lumio.Sample.Bots.csproj` | FAIL，`SAMPLE_BOTS_CLIENT_BOT_MISSING`；SDK 报告 `ubuntu.24.04-x64`，发布物没有同名目录 |
| `dotnet build Client/Bots/Lumio.Sample.Bots.csproj -p:NETCoreSdkRuntimeIdentifier=linux-x64` | PASS，0 warnings / 0 errors；仅验证托管编译，不改变启动器识别的本机 RID |
| `node Engine/tools/verify-release.mjs --root Engine --rid linux-x64 --version 0.0.2 --json` | PASS，249 files |

为避开机器上已有的同名测试栈，使用发布物的 Compose 文件，设置 `LUMIO_GAME_PLATFORM_DIR` 指向此次检出的 `Tools/compose`、`LUMIO_PLATFORM_HOST_PORT=38080`，以独立项目 `lumio-handbook-tour-20260927` 执行 `docker compose -f Engine/platform/docker-compose.yml -p lumio-handbook-tour-20260927 up -d`。Platform 容器启动后执行：

```sh
node Tools/launcher.mjs --bots 2 --stagger-ms 250 --origin http://127.0.0.1:38080 --scenario-dll Client/Bots/bin/Debug/net10.0/Lumio.Sample.Bots.dll
```

启动器 **exit 2、`VERIFICATION_STATUS=BLOCKED_ENV`**，日志与 `verification.json` 一致：

| 步骤 | 状态 | 日志摘要 |
| --- | --- | --- |
| 01 | READY | `LumioConfig export + typed Reader via M9 loader`；这是就绪标记，不是本次执行配表 CLI 的证明 |
| 02–14 | BLOCKED_ENV（每步均输出） | `this machine is ubuntu.24.04-x64, and Engine/manifest.json (v0.0.2) ships only [win-x64, linux-x64]` |

`Tools/engine-release.mjs` 从 `dotnet --info` 读取 RID，再与 manifest 精确匹配。此次未进入登录、DS/Bot 运行或存档恢复；没有靠改变运行时 RID 绕过检查。随后对自己的 Compose 项目执行 `down --volumes`，核对容器已清理。原有项目没有被本次命令管理。

**未执行**：浏览器 WebGL2 画面验收、真实 Platform/DS/Bot 联机业务、跨进程存档恢复、两轮世界哈希对账、配表 CLI 实际导出、引擎升级脚本的实际切换、Agent 客户端安装验收和完整 Windows/Linux 运行矩阵。

完整导览入口和 14 步逐项阅读路径见 [入门](skills/lumio-development/references/getting-started.md#十四步逐步索引)；执行后应保留启动器摘要、DS 日志、Bot 生命周期日志、非空完整 `result.ndjson`，以及第 14 步同一存储重启的核对结果。

## 上游缺口

| 缺口 | 当前证据与影响 |
| --- | --- |
| v0.0.2 没有地图 capture CLI | 发布物 `tools/` 不含 `capture-voxel.mjs`；Sample `Tools/capture-basemap.mjs` 明确检查它。可以加载随 Sample 提交的底图，重新制作底图的发布入口尚未提供。 |
| v0.0.2 的 `server/` 没有启动配置样例 | 目录只有运行物及 deps/runtimeconfig/build-info 等 JSON。手册使用 Sample 的 `Server/Config/Startup/server.json` 并核对发布物 HostEntry，未声称在发布包找到了不存在的样例。 |
| 部分公共错误码解释不够具体 | 包内 `error-codes.md` 虽列出 257/257，`checkpoint_corrupt_manifest` 等仍用泛化说明，`checkpoint_incomplete_group` 依赖规则名；手册挑常见码解释，完整表链接到公开包。 |
| Sample 部分文字落后于代码 | README 仍说 Engine 尚未钉版本；Tools README 仍称六份 Reader，脚本实际复制八份。手册按 gitlink 和脚本修正。 |
| 示例没有展示全部玩法能力 | 箱子的场景/UI、火花创建与渲染、GAS 标签、预测拾取、通用建造、模型导入和在线配表更新尚未提供完整 Sample 流程；各页明确说明。 |
| 矿脉绑定被拒绝后没有立即重试 | `Gameplay/SampleMiningComponent.Server.cs` 的 `CompletePendingBind` 没有消费 `TryStageMutation` 的返回结果便清理待绑定记录，修订冲突后不会立即重新扫描。未修改 Sample，也未承诺自动恢复。 |
| 本机 Linux RID 不在发布名单 | Bot 工程直接使用 `NETCoreSdkRuntimeIdentifier` 拼目录，启动器按 `dotnet --info` 精确比较 RID；此环境的 `ubuntu.24.04-x64` 被拒绝。编译参数覆盖不能替代运行支持。 |
| Spectator 的上游短命令缺少导览前提 | 只运行 `node Tools/launcher.mjs --spectator` 未提供场景程序集；手册列出既有完整导览命令及 `--spectator` 参数。 |
| DevKit Windows 原生安装器更新失败 | 本分支及未修改 main 均有上述三个相同错误；WSL/Linux 测试通过。记录为仓内既有问题，未扩展本次手册任务去改安装实现。 |

## Sample 路径、类名与命令核对表

以下表格按最终正文逐项核对。路径使用 `git cat-file -e origin/main:<path>`，类型、方法和命令入口使用 `git grep -n -F <name> origin/main -- <path>`；每个路径都以完整拼写核对，目录省略末尾斜线，生成的运行文件另列说明。


已逐项检查下表的路径及名称/声明，均存在。类型用途与调用顺序还对照了对应实现；运行结果另见前面的实测记录。

| Sample 路径 | 核对的类名、方法或声明 | 结果 |
| --- | --- | --- |
| `.github/workflows/tour.yml` | `LumioEcsSide`、`LumioSample.slnx` | 存在 |
| `Client` | 文件或目录 | 存在 |
| `Client/Assets/Blocks` | 文件或目录 | 存在 |
| `Client/Assets/Blocks/ATTRIBUTION.md` | 文件或目录 | 存在 |
| `Client/Assets/Blocks/LICENSE` | 文件或目录 | 存在 |
| `Client/Assets/Blocks/README.md` | 文件或目录 | 存在 |
| `Client/Assets/Blocks/SOURCES.md` | 文件或目录 | 存在 |
| `Client/Assets/Blocks/lumio.stone.json` | 文件或目录 | 存在 |
| `Client/Assets/Blocks/lumio.torch.json` | 文件或目录 | 存在 |
| `Client/Assets/Blocks/pack.json` | 文件或目录 | 存在 |
| `Client/Assets/Blocks/preview/blocks-preview.png` | 文件或目录 | 存在 |
| `Client/Assets/Blocks/source/generate-textures.mjs` | 文件或目录 | 存在 |
| `Client/Assets/Blocks/source/kenney` | 文件或目录 | 存在 |
| `Client/Assets/Blocks/textures` | 文件或目录 | 存在 |
| `Client/Assets/Blocks/textures/stone.png` | 文件或目录 | 存在 |
| `Client/Bots` | 文件或目录 | 存在 |
| `Client/Bots/Lumio.Sample.Bots.csproj` | 文件或目录 | 存在 |
| `Client/Bots/SampleMiningPlan.cs` | `Issue`、`Read` | 存在 |
| `Client/Bots/SampleMiningScenario.cs` | `Accepted`、`Available`、`BotInputKind.ChatInput`、`BotInputTerm`、`BotIssueResult`、`BotIssuedCommand.Chat`、`HasSelf`、`MineAbility`、`MoveAbility`、`Reason`、`SampleMiningScenario`、`TryGet`、`Vocabulary` | 存在 |
| `Client/Bots/SampleRestoreVerifyScenario.cs` | `SampleRestoreVerifyScenario` | 存在 |
| `Client/Config/Generated` | 文件或目录 | 存在 |
| `Client/Config/Generated/AttributesTable.cs` | 文件或目录 | 存在 |
| `Client/Config/Generated/MapTable.cs` | 文件或目录 | 存在 |
| `Client/Config/Generated/MiningTable.cs` | 文件或目录 | 存在 |
| `Client/Config/Generated/MovementTable.cs` | `StepMeters` | 存在 |
| `Client/Config/Tables` | 文件或目录 | 存在 |
| `Client/Tests/Chat/ChatPipelineTests.cs` | `ChatComponent`、`Point` | 存在 |
| `Client/UI` | 文件或目录 | 存在 |
| `Client/UI/Spectator/Directory.Build.props` | 文件或目录 | 存在 |
| `Client/UI/Spectator/README.md` | 文件或目录 | 存在 |
| `Client/UI/Spectator/SpectatorDump.cs` | `ToHex`、`Vector3` | 存在 |
| `Client/UI/Spectator/host/Lumio.Sample.Client.Spectator.csproj` | 文件或目录 | 存在 |
| `Client/UI/Spectator/main.js` | 文件或目录 | 存在 |
| `Client/UI/Spectator/main.test.mjs` | `SectionRevision` | 存在 |
| `Directory.Build.props` | 文件或目录 | 存在 |
| `Directory.Build.targets` | `**/*.Client.cs`、`**/*.Server.cs`、`LUMIO_SDK_UNRESOLVED`、`LumioEcsGenerate`、`LumioEcsSide` | 存在 |
| `Gameplay` | 文件或目录 | 存在 |
| `Gameplay/Abilities` | 文件或目录 | 存在 |
| `Gameplay/Abilities/MineAbility.Client.cs` | `BindingGet`、`BlockId`、`ClassifyPredictedDig`、`HasBlockId`、`OrderFinalDig`、`PredictedDigVerdict`、`Prediction`、`SampleMiningComponent`、`TryLocate`、`TryReadSectionBindings`、`TryStageDigThrough`、`VoxelCellQuery`、`VoxelGameplayBinding.Resolve`、`VoxelStageResult`、`VoxelStageStatus.Staged` | 存在 |
| `Gameplay/Abilities/MineAbility.Server.cs` | `OrderFinalDig`、`StageFinal` | 存在 |
| `Gameplay/Abilities/MineAbility.cs` | `AbilityType`、`AdmitTarget`、`AwaitAuthority`、`CanActivate`、`ClassifyPredictedDig`、`Execute`、`GetBaseValue`、`Input`、`MineAbility`、`Order`、`OrderFinalDig`、`PredictedDigVerdict`、`PredictionKind.LogicPredict`、`Refuse`、`SampleConfigBinding.For`、`SetBaseValue`、`SetCooldown`、`Stamina`、`TargetHex`、`WithinReach` | 存在 |
| `Gameplay/Abilities/MoveAbility.cs` | `AbilitySweepHit`、`IAbilityPhysicsPort`、`SweepBox`、`TravelFraction`、`physics_invalid_query`、`physics_unavailable` | 存在 |
| `Gameplay/Abilities/PickupAbility.Server.cs` | `Amount`、`Effects.Apply`、`ExecuteCore`、`OrePileComponent`、`PickupOreEffect.Parameters`、`World.Commands.Destroy` | 存在 |
| `Gameplay/Abilities/PickupAbility.cs` | `AuthorityOnly`、`CanActivate`、`Execute`、`ExecuteCore`、`Input`、`IsLiveDrop`、`PickupAbility`、`TargetHex`、`WithinReach`、`pickup_invalid_target`、`pickup_out_of_reach`、`pickup_target_gone` | 存在 |
| `Gameplay/Components` | 文件或目录 | 存在 |
| `Gameplay/Components/Box` | 文件或目录 | 存在 |
| `Gameplay/Components/Box/BoxComponent.Server.cs` | `BoxComponent`、`Close`、`NetEntityId`、`Open` | 存在 |
| `Gameplay/Components/Box/BoxComponent.cs` | `BoxComponent`、`Component`、`EcsComponent`、`Inventory`、`Locked`、`Name`、`Openers`、`Persist`、`Scope.Aoi`、`Scope.Claim`、`Scope.None`、`Sync`、`SyncList`、`claimBy`、`granted`、`revoked` | 存在 |
| `Gameplay/Components/Chat` | 文件或目录 | 存在 |
| `Gameplay/Components/Chat/ChatComponent.Client.cs` | `OnChatMessage`、`Say`、`SendMessage` | 存在 |
| `Gameplay/Components/Chat/ChatComponent.Server.cs` | `GetByteCount`、`LastMessageText`、`LastMessageTick`、`OnChatMessage`、`Scope.None`、`SendMessage` | 存在 |
| `Gameplay/Components/Chat/ChatComponent.cs` | `ChatComponent`、`ClientRpc`、`OnChatMessage`、`Scope.Room`、`SendMessage`、`ServerRpc`、`chat.input` | 存在 |
| `Gameplay/Components/Fx/MiningSparkComponent.Client.cs` | `Component`、`MiningSparkComponent` | 存在 |
| `Gameplay/Components/Identity/IdentityComponent.cs` | `Authority.Owner`、`Authority.Server`、`ColorHue`、`Name`、`Scope.Room` | 存在 |
| `Gameplay/Components/Mining/PendingDigComponent.cs` | `PendingDigComponent`、`Persist`、`Scope.None`、`Serial` | 存在 |
| `Gameplay/Components/Ore/OrePileComponent.cs` | `Amount`、`Scope.Room` | 存在 |
| `Gameplay/Components/Vein/VeinReserveComponent.cs` | `Remaining`、`Scope.Aoi`、`VeinReserveComponent` | 存在 |
| `Gameplay/Config/ConfigBindings.Client.cs` | 文件或目录 | 存在 |
| `Gameplay/Config/ConfigBindings.Server.cs` | 文件或目录 | 存在 |
| `Gameplay/Config/SampleConfigBinding.cs` | `ActivateAtBarrier`、`ConfigModule.Create`、`ConfigSnapshotId`、`CreateSnapshot`、`CreateTypedTables`、`ErrorMessage`、`For(World`、`GeneratedRegistry.Instance`、`IGameConfigExportBinding`、`ISampleConfig`、`IsSuccess`、`LumioConfigLoader.Load`、`Project(`、`RequiredTables`、`SampleConfigBinding`、`Stage(`、`WorldConfigBinding` | 存在 |
| `Gameplay/Config/SampleTables.cs` | `LUMIO_CONFIG_DIR`、`ResolveDirectory`、`SampleTables` | 存在 |
| `Gameplay/Config/SampleTypedTables.cs` | `SampleTypedTables`、`TryGetTable`、`public static ITypedTableSet Create` | 存在 |
| `Gameplay/Effects` | 文件或目录 | 存在 |
| `Gameplay/Effects/PickupOreEffect.cs` | `Amount`、`Apply`、`EffectSettlementContext`、`EffectType`、`EffectTypeCatalog`、`GetBase`、`GetBaseValue`、`Instant`、`Parameters`、`PickupOreEffect`、`Register`、`TypeId` | 存在 |
| `Gameplay/EntityTypes` | 文件或目录 | 存在 |
| `Gameplay/EntityTypes/BoxEntity.cs` | `BlockEntity`、`BoxComponent`、`BoxEntity`、`EntityType`、`Has`、`Mode.CS` | 存在 |
| `Gameplay/EntityTypes/MiningSparkEntity.Client.cs` | `MiningSparkComponent`、`MiningSparkEntity`、`Mode.Local` | 存在 |
| `Gameplay/EntityTypes/OreDropEntity.cs` | `OreDropEntity`、`OrePileComponent` | 存在 |
| `Gameplay/EntityTypes/PlayerEntity.cs` | `AbilityComponent`、`AttributeComponent`、`DeclareAttribute`、`EffectComponent`、`LogicTransform`、`ObserverComponent`、`Ore`、`PlayerEntity`、`Stamina` | 存在 |
| `Gameplay/EntityTypes/VeinEntity.cs` | `VeinEntity`、`VeinReserveComponent` | 存在 |
| `Gameplay/EntityTypes/WorldEntity.cs` | `TickRateHz`、`WorldEntity` | 存在 |
| `Gameplay/Lumio.Sample.Gameplay.csproj` | `Lumio.Sample.Gameplay` | 存在 |
| `Gameplay/SampleGameplay.cs` | `AbilityActivationContext`、`ActivationContextFactory`、`BindPlayer`、`CurrentOwner`、`PickupOreEffect.Register`、`RegisterCatalog`、`SampleAbilityAdmission`、`SampleGameplay` | 存在 |
| `Gameplay/SampleMiningComponent.Client.cs` | `TryLocate`、`TryReadSectionBindings` | 存在 |
| `Gameplay/SampleMiningComponent.Server.cs` | `Advance`、`Amount`、`DigApplied`、`DrainResults`、`OreDropEntity`、`Pay`、`PendingDigComponent`、`Settle`、`StageFinal`、`TryStageCoalescibleDigThrough`、`World.Commands`、`World.Commands.Create`、`mining_applied`、`mining_refused`、`mining_reward`、`mining_stage` | 存在 |
| `Gameplay/SampleMiningSystem.Server.cs` | `Advance`、`EcsSystem`、`Execute`、`SampleMiningComponent`、`SampleMiningSystem`、`Single`、`System`、`TickPhase.ProcessorPlan`、`World` | 存在 |
| `Gameplay/Tables` | 文件或目录 | 存在 |
| `Gameplay/Tables/README.md` | 文件或目录 | 存在 |
| `Gameplay/Tables/profiles/acceptance` | 文件或目录 | 存在 |
| `Gameplay/Tables/profiles/acceptance/layers/environment/map.txt` | 文件或目录 | 存在 |
| `Gameplay/Tables/registry` | 文件或目录 | 存在 |
| `Gameplay/Tables/registry/row-ids.json` | 文件或目录 | 存在 |
| `Gameplay/Tables/registry/tombstones.json` | 文件或目录 | 存在 |
| `Gameplay/Tables/repository.yaml` | 文件或目录 | 存在 |
| `Gameplay/Tables/schemas/movement.json` | `step_meters` | 存在 |
| `Gameplay/Tables/tables/movement.txt` | 文件或目录 | 存在 |
| `Gameplay/generated` | 文件或目录 | 存在 |
| `Gameplay/generated/client` | 文件或目录 | 存在 |
| `Gameplay/generated/client/BoxComponent.g.cs` | `BoxComponent` | 存在 |
| `Gameplay/generated/client/BoxEntity.Template.g.cs` | `BoxComponent`、`BoxEntityTemplate` | 存在 |
| `Gameplay/generated/client/GeneratedAbilityRegistry.g.cs` | `GeneratedAbilityRegistry`、`MineAbility`、`MoveAbility`、`PickupAbility`、`RegisterAll` | 存在 |
| `Gameplay/generated/client/GeneratedEffectRegistry.g.cs` | `GeneratedEffectRegistry`、`PickupOreEffect`、`TypeIdOf` | 存在 |
| `Gameplay/generated/client/Lumio.Sample.Gameplay.Registry.g.cs` | `BlockEntityTypes`、`BoxEntity`、`DeclaredTickRateHz`、`GeneratedRegistry`、`VeinEntity`、`WorldEntity`、`WorldEntityType` | 存在 |
| `Gameplay/generated/client/MiningSparkEntity.Template.g.cs` | `MiningSparkEntityTemplate` | 存在 |
| `Gameplay/generated/server` | 文件或目录 | 存在 |
| `Gameplay/generated/server/BoxComponent.g.cs` | `BoxComponent` | 存在 |
| `Gameplay/generated/server/BoxEntity.Template.g.cs` | `BoxComponent`、`BoxEntityTemplate` | 存在 |
| `Gameplay/generated/server/GeneratedAbilityRegistry.g.cs` | `GeneratedAbilityRegistry`、`MineAbility`、`MoveAbility`、`PickupAbility`、`RegisterAll` | 存在 |
| `Gameplay/generated/server/GeneratedEffectRegistry.g.cs` | `GeneratedEffectRegistry`、`PickupOreEffect`、`TypeIdOf` | 存在 |
| `Gameplay/generated/server/Lumio.Sample.Gameplay.Registry.g.cs` | `BlockEntityTypes`、`BoxEntity`、`ChatComponent`、`DeclaredTickRateHz`、`GeneratedRegistry`、`SampleMiningSystem`、`SendMessage`、`TickPhase.ProcessorPlan`、`VeinEntity`、`WorldEntity`、`WorldEntityType`、`chat.input` | 存在 |
| `LICENSE` | 文件或目录 | 存在 |
| `LumioSample.slnx` | 文件或目录 | 存在 |
| `NuGet.config` | 文件或目录 | 存在 |
| `README.md` | `LumioEcsSide`、`LumioSample.slnx` | 存在 |
| `Server` | 文件或目录 | 存在 |
| `Server/Assets/Maps` | 文件或目录 | 存在 |
| `Server/Assets/Maps/bot-voxel-budget.json` | 文件或目录 | 存在 |
| `Server/Assets/Maps/official-catalog.json` | 文件或目录 | 存在 |
| `Server/Assets/Maps/sample.layout.json` | 文件或目录 | 存在 |
| `Server/Assets/Maps/sample.voxel` | 文件或目录 | 存在 |
| `Server/Config/Generated` | 文件或目录 | 存在 |
| `Server/Config/Generated/AttributesTable.cs` | 文件或目录 | 存在 |
| `Server/Config/Generated/MapTable.cs` | 文件或目录 | 存在 |
| `Server/Config/Generated/MiningTable.cs` | 文件或目录 | 存在 |
| `Server/Config/Generated/MovementTable.cs` | 文件或目录 | 存在 |
| `Server/Config/Profiles/acceptance` | 文件或目录 | 存在 |
| `Server/Config/Startup/server.acceptance.json` | 文件或目录 | 存在 |
| `Server/Config/Startup/server.json` | 文件或目录 | 存在 |
| `Server/Config/Tables` | 文件或目录 | 存在 |
| `Server/Config/Tables/origins.json` | 文件或目录 | 存在 |
| `Server/Tests/Gameplay/BoxComponentTests.cs` | `BoxComponent`、`Close`、`Open` | 存在 |
| `Tools` | 文件或目录 | 存在 |
| `Tools/capture-basemap.mjs` | 文件或目录 | 存在 |
| `Tools/check-block-assets.mjs` | 文件或目录 | 存在 |
| `Tools/check-block-assets.test.mjs` | 文件或目录 | 存在 |
| `Tools/launcher.mjs` | `BLOCKED_ENV`、`DS_READY` | 存在 |
| `Tools/sync-config-export.mjs` | 文件或目录 | 存在 |
| `Tools/sync-config-readers.mjs` | `LUMIO_CONFIG_ROOT`、`LUMIO_PYTHON`、`READER_FILES` | 存在 |
| `Tools/tour-steps.mjs` | 文件或目录 | 存在 |
| `Tools/update-engine.mjs` | 文件或目录 | 存在 |
| `global.json` | 文件或目录 | 存在 |

### 命令、子模块和生成路径

| 引用 | 核对来源 | 结果 |
| --- | --- | --- |
| `git clone --recursive`、`git submodule update --init --depth 1 Engine` | Sample `README.md`、`Directory.Build.targets` | 原命令存在；已在干净目录取得固定版本 |
| `node Tools/update-engine.mjs <版本>` | `Tools/update-engine.mjs` 的用法、版本解析与发布物核对 | 入口及参数存在；升级切换未执行 |
| `dotnet build LumioSample.slnx`、客户端 `-p:LumioEcsSide=client`、Bot build、`dotnet test LumioSample.slnx` | `README.md`、`.github/workflows/tour.yml` | 命令存在；build 结果见实测，Sample test 未执行 |
| `node Tools/launcher.mjs --bots 2 --stagger-ms 250 --scenario-dll Client/Bots/bin/Debug/net10.0/Lumio.Sample.Bots.dll` | `README.md`、`.github/workflows/tour.yml`、`Tools/launcher.mjs` | 命令与选项存在；本次另加 `--origin` 使用隔离平台，结果 BLOCKED_ENV |
| 导览命令附加 `--spectator` | `Tools/launcher.mjs` 的参数解析与帮助；`Client/UI/Spectator/README.md` | 选项存在；浏览器运行未执行 |
| `dotnet build Gameplay/Lumio.Sample.Gameplay.csproj -c Release -p:LumioEcsSide=client -p:LumioBrowserReplica=true` | `Client/UI/Spectator/README.md` | 原命令存在，未执行 |
| `dotnet publish Client/UI/Spectator/host/Lumio.Sample.Client.Spectator.csproj -c Release -p:LumioEcsSide=client -p:LumioBrowserReplica=true` | `Client/UI/Spectator/README.md` | 原命令存在，未执行 |
| `node Tools/sync-config-export.mjs`、`node Tools/sync-config-readers.mjs`，以及各自的 `--check` | `Gameplay/Tables/README.md` 与两个脚本 | 四条命令存在，八个 Reader 清单已核对；未执行导出 |
| `node Client/Assets/Blocks/source/generate-textures.mjs`、`node Tools/check-block-assets.mjs`、`node --test Tools/check-block-assets.test.mjs` | `Client/Assets/Blocks/README.md` | 三条原命令存在；仅资产检查实际执行并 PASS |
| `lumio-ds --check-config` | `Tools/launcher.mjs` 的 DS 启动前调用 | 参数存在；本次未进入此阶段 |
| `Engine` | `git ls-tree origin/main Engine` | `160000 commit 9e57979049fe727e02992ad48116ce1324a42277`；gitlink 的目标在子模块仓，不把主仓 `cat-file` 找不到该对象当作文件缺失 |
| `Tools/engine-release.mjs` | `git cat-file -e`、`git grep`：`hostRid`、`parseDotnetRid`、`assertPlatform` | 存在；解释此次 RID 预检结果 |
| `Gameplay/bin/Debug/net10.0/Lumio.Sample.Gameplay.dll`、`Client/Bots/bin/Debug/net10.0/Lumio.Sample.Bots.dll` | 各自 `.csproj`、`Directory.Build.props` 和本次 build 日志 | 构建输出，存在；不是 Git 源文件 |
| `Client/UI/Spectator/host/bin/Release/net10.0/publish/wwwroot`、`wwwroot/game-assets/Blocks/`、`_framework/` | Spectator 的 `.csproj`、README 与发布资源配置 | 发布路径已核对；本次没有生成浏览器输出 |
| `.run/` 中的 `verification.json`、`lumio-ds*.log`、`ds-boot-1/`、`ds-boot-2/`、`server.boot-1.json`、`server.boot-2.json`、`bot-1/`、`bot-verify/` | `Tools/launcher.mjs`、`Tools/tour-steps.mjs` | 运行产物名称和消费路径存在；本次只有预检摘要，不冒称生成了 DS/Bot 业务日志 |
| `Server/Diagnostics/Logs/` | `Server/Config/Startup/server.json` 的 `logging.dir` | 运行目录；不是跟踪的源码目录 |
| `config/manifest.json` | `Gameplay/Config/SampleTables.cs`、Gameplay `.csproj` | 程序集旁配置副本；浏览器配置则由 Spectator `Directory.Build.props` 嵌入 |

LumioConfig CLI 另在其固定 `origin/main` 的 `tools/lumio_config.py`、`src/lumio_config/cli.py` 以及 `docs/reference/cli.md` 核对：`validate --root/--json`、`format --check --root`、`registry verify --root`、`query schema`、`query row`、`patch validate`、`preview`、`patch apply`、`export --client-out/--server-out/--csharp-out` 都有对应解析入口；本次仅静态核对。泛称的 `<table>`、`<name-or-id>` 是参数占位符；Schema 和 Reader 路径用表中的 movement 与四张表实际展开核对。

### SDK 公共参考与代码摘录

| 引用 | v0.0.2 发布物证据 |
| --- | --- |
| HostEntry 类型与方法 | Sample `server.json` 包含 `Lumio.Server.HostEntry.HostEntry, Lumio.Server.HostEntry` / `LumioHostEntry`；发布物两平台 `server/<rid>/Application/Lumio.Server.HostEntry.dll` 存在 |
| `BlockId`、`VoxelCellQuery`、`VoxelWriteEntry` | SDK 的 Coordination XML 中构造签名使用 `System.UInt32`；Sample `MineAbility` 的 `uint blockId` 消费面一致 |
| 13 个 `TickPhase`、系统登记限制、GAS 结算顺序 | v0.0.2 SDK 的 Primitives/Ecs/Simulation XML 名称与发布 manifest 对应的实现核对；只总结调用行为，没有复制实现或内部文档 |
| `Lumio.Engine.SDK.xml`、`Lumio.GameRuntime.Ecs.xml`、`Lumio.GameRuntime.Gas.xml`、`Lumio.GameRuntime.Primitives.xml`、`Lumio.GameRuntime.Simulation.xml`、`Lumio.GameRuntime.Config.xml` | 均在 SDK 包 `lib/net10.0/` 中，已检查 ZIP 条目 |
| 常见关闭原因与错误码 | 已逐项对照包内 `content/wire/ds-transport-v1.json`、`content/docs/error-codes.md` 和发布物 `web/ds-close-codes.mjs`；完整表公开包链接可达 |
| `content/wire/block-asset-v1.json` | SDK 随包方块资产格式；描述实例取自 Sample 的 `Client/Assets/Blocks/lumio.stone.json` |

最终 12 段 C#/JSON 摘录逐段匹配对应 Sample 原文，仅允许去除外层缩进与统一换行；没有自编 API 片段。`NOTICE.md` 列出来源与许可证，随包许可证与 Sample 对应原文件逐字节一致。36 篇手册 Markdown 的本地文件链接、锚点和单一页脚已检查；这次人工核对使用的临时记录没有加入仓库，未新增 CI 门或检测工具。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对、编译、启动预检；完整导览未通过）
