# 方块材质与世界表现

美术资源决定世界对象如何显示，方块和实体仍分别负责地形与游戏逻辑。

## 用箱子看资源分工

1. 箱子占格的方块提供外观。
2. `BoxEntity` 携带 `BoxComponent` 保存库存逻辑，两者通过格子引用相连。
3. 玩家操作箱子时由玩法改变状态；美术资源显示对应状态。
4. 挖掘火花等纯客户端表现可以使用本地实体。

实体声明见 [实体与组件](../../lumio-gameplay/references/entities-and-components.md)。外观不决定服务器碰撞、伤害或同步。

## Sample 的方块资产

[Client/Assets/Blocks/](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Client/Assets/Blocks/README.md) 保存方块描述、贴图、可重做的源与来源记录。方块目录中的 `asset://blocks/lumio.stone` 对应 `Client/Assets/Blocks/lumio.stone.json`。

以下原文摘自 `Client/Assets/Blocks/lumio.stone.json`，提交 `f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb`；该目录按 [CC0-1.0](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Client/Assets/Blocks/LICENSE) 发布：

```json
{
  "format": "lumio.block-asset.v1",
  "faces": {
    "all": "textures/stone.png"
  }
}
```

`faces` 指六个方块面的贴图，可使用共同贴图或逐面覆盖；`cross` 是草和火把等交叉面片的贴图，不是“第七个方块面”。`pack.json` 声明整包贴图边长，Sample 当前为 128 × 128。原木顶底和侧面、草方块顶侧底可用不同贴图。

贴图放在 `textures/`。整包按最近邻采样；镂空与半透明按方块材质类别处理。替换资源时同时检查描述、透明度、来源记录和目录引用，步骤见 [资产生产](asset-production.md)。

## WebGL2 三维视图

Sample 的 spectator（浏览器旁观客户端）提供 WebGL2 三维方块视图。发布时把资源复制到 `wwwroot/game-assets/Blocks/`，把引擎渲染模块复制到相应目录；用 [客户端搭建](../../lumio-client/references/setup.md) 的发布和启动步骤，再打开打印的地址并加 `?view=blocks`。

## 当前边界

- 当前方块描述不提供动画条带；水和岩浆使用静态贴图。
- 面贴图按方块种类选取，不随 BlockState（同种方块的状态值）变化；门、台阶等需按现有规则设计。
- 通用实体模型、骨骼与动画导入流程在示例中尚未提供，不能从“页面能画实体”推断已经接线。
- 缺发布 bundle、WASM 或 WebGL2 浏览器属于缺运行环境；描述正确但没有消费映射属于尚未接线。

来源：[方块资源说明](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Client/Assets/Blocks/README.md)、[发布工程](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Client/UI/Spectator/host/Lumio.Sample.Client.Spectator.csproj)。实际验收见 [接入与验收](integration-and-review.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
