# 项目布局与开发规范

这页说明共享玩法怎样放文件、怎样拆服务器和客户端，以及哪些文件由生成器维护。

例如给箱子增加服务器逻辑：

1. 先找到 `Gameplay/EntityTypes/BoxEntity.cs` 的实体声明。
2. 在 `Gameplay/Components/Box/` 维护组件数据，需要分端时使用对应后缀文件。
3. 构建两端并检查生成注册表，再在游戏中验证交互。

## Sample 的实际布局

```text
my-game/
  Gameplay/                       # 两端共享的实体、组件、技能与效果
    EntityTypes/
    Components/Chat/
    Abilities/
    Effects/
    generated/                    # SDK 生成的注册表和绑定
  Server/                         # DS 配置、表导出、地图和服务器测试
    Config/Startup/server.json
    Config/Tables/
    Assets/Maps/
  Client/                         # 客户端表、方块资产、Bot 和 UI
    Config/Tables/
    Assets/Blocks/
    Bots/
    UI/
  Tools/                          # launcher、engine update、资产检查和测试脚本
  .run/                           # 被 gitignore 的日志、存档和本次证据
```

结构依据 [Sample 源树](https://github.com/LumioGames/LumioSample/tree/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb)；新游戏可沿用，但不要为了符合示意图搬动已有项目。

## 共享 Gameplay 如何拆两端

| 文件 | 作用 | 构建侧 |
| --- | --- | --- |
| `Gameplay/EntityTypes/PlayerEntity.cs`、`Gameplay/Components/Chat/ChatComponent.cs` | 实体/组件/RPC 的共享声明 | 两端 |
| `*.Server.cs` | 服务器确认的业务、数据修改和 RPC（远程调用）实现 | 服务器 |
| `*.Client.cs` | 输入、客户端表现和预测实现 | 客户端 |
| `Gameplay/generated/client/**`、`Gameplay/generated/server/**` | 生成的注册表、同步绑定和模板 | 由 SDK 生成，不能手改 |
| `Server/Config/Startup/server.json` | DS 入口和存档/体素配置模板 | 服务器运行时 |
| `Server/Assets/Maps/**` | 底图、目录和地图说明 | 服务器/作者工具 |

Sample 的 `Directory.Build.targets` 用 `LumioEcsSide=client` 选择客户端，并排除另一端的后缀文件；默认构建是服务器侧。同一个分部类型的文件保持相同 namespace（命名空间）、类型名和 partial（分部类）声明。ID（稳定编号）用于识别网络中的类型，不能靠文件排序改变。

## 新增声明的步骤

1. 在 `Gameplay/EntityTypes/` 或 `Gameplay/Components/Chat/` 添加共享声明。
2. 需要服务器逻辑时添加同名 `.Server.cs`；需要输入/表现时添加 `.Client.cs`。
3. 用 [Gameplay 指引](../../lumio-gameplay/SKILL.md) 的代码生成命令构建两侧，检查 `Gameplay/generated/{server,client}/` 的新注册表。
4. 分别构建服务器与客户端，确认生成程序集落在不同输出目录。
5. 用真实 DS/Bot 或浏览器场景核对实体、同步和表现。

生成物不得手改。变更声明、字段、RPC 或属性声明后，重新运行项目已有生成器并把生成结果与源一起提交。

## 相关入口

- [实体与组件](../../lumio-gameplay/references/entities-and-components.md)
- [同步与 RPC](../../lumio-gameplay/references/sync-and-rpc.md)
- [代码生成](../../lumio-gameplay/references/code-generation.md)
- [服务器配置](../../lumio-server/references/setup.md)
- [客户端构建](../../lumio-client/references/setup.md)

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
