# 体素、材质、实体模型与世界表现

先判世界职责，再决定美术资源：世界只有体素和实体；模型、纹理、动画是它们的表现。

## 按职责交付

| 需求 | 世界对象 | 美术交付 |
| --- | --- | --- |
| 静态地形、石头、地面 | 体素 | 方块描述、七面贴图、尺度和拼接说明 |
| 玩家、掉落矿石、移动物体 | 实体 | 模型/图标、朝向、尺度、状态表现 |
| 固定占格但带库存的箱子 | 占格体素 + `BoxEntity`/`BoxComponent` | 占格外观和开关状态；库存由玩法实体处理 |
| 只在客户端出现的火花或提示 | Local Entity | 创建/结束条件、跟随对象和清理方式 |

不要把库存、耐久或脚本塞进 `BlockId`；也不要给每个普通地形格造实体。

## Sample 的方块资产契约

公开 Sample 的方块资产位于 `Client/Assets/Blocks/`，每个 `lumio.<id>.json` 描述方块的 `format`、七面贴图来源和可选许可证；`pack.json` 声明贴图尺寸。贴图放在同目录的 `textures/`，源和可复现导出脚本在 `source/`。这是消费端契约，不是任意图片目录。

从源修改后重新生成并验收：

```sh
node Client/Assets/Blocks/source/generate-textures.mjs
node Tools/check-block-assets.mjs
```

`check-block-assets.mjs` 会读取 `Client/Assets/Blocks/pack.json`、描述 JSON、贴图路径和 PNG 尺寸；失败时先修描述或源，不手改生成预览绕过检查。许可证和第三方来源写在 `ATTRIBUTION.md`、`SOURCES.md`，不要把未授权参考图放进运行包。

## WebGL2 表现检查

Sample spectator 的浏览器渲染路径使用 WebGL2。构建发布的 spectator bundle 后，通过 HTTP(S) 打开 `Client/UI/Spectator/host/bin/Release/net10.0/publish/wwwroot`，在真实页面核对：

1. 方块描述能映射到 `asset://blocks/<id>` 对应的 `Blocks/<id>.json`。
2. 缺贴图时页面报告资源警告并保持可见的错误状态，不把紫黑占位当作通过。
3. 深浅背景、透明方块、镂空方块和相邻面在实际视口中没有错误裁切。
4. 浏览器 Console/Network 没有新增资源加载错误。

只有静态 JSON 通过或设计软件能打开，不能证明 WebGL2 页面已加载；缺 `_framework/`、WASM 或发布 bundle 时记录“缺运行环境”。

## 实体表现

先找项目里已经工作的实体加载点，再对齐世界单位、原点、朝向、挂点、动画状态和生命周期。模型外观不决定服务器碰撞、伤害或同步；这些由 Gameplay/GAS 和实体组件决定。

## 证据边界

- **能力不存在**：当前发布物没有所需格式或导入入口。
- **尚未接线**：方块描述存在，但客户端没有消费映射。
- **缺运行环境**：缺 WebGL2 发布 bundle、WASM 或目标浏览器。
- **本次未验证**：未执行浏览器页面或真实场景检查。

接入步骤见 [接入与验收](integration-and-review.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对 / 编译 / 真实运行）
