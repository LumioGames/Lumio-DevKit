# 资产生产、来源与交接

先保留可修改的源和来源记录，再导出到客户端实际读取的位置。

## 沿 Sample 的资源目录制作

| Sample 路径（相对 `Client/Assets/Blocks/`） | 用途 |
| --- | --- |
| `source/generate-textures.mjs` | 自绘、派生贴图与预览的生成源。 |
| `source/kenney/` | 派生贴图使用的原图。 |
| `textures/` | 客户端使用的 PNG。 |
| `lumio.stone.json` 等描述 | 把方块面映射到贴图。 |
| `pack.json` | 格式、整包边长与许可说明。 |
| `preview/blocks-preview.png` | 方块对照预览。 |
| `SOURCES.md` / `ATTRIBUTION.md` | 每张图的来源、许可、修改和署名。 |

先改生成源或描述，再执行 [Client/Assets/Blocks/README.md](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Client/Assets/Blocks/README.md) 的命令（该目录按 CC0-1.0 发布）：

```sh
node Client/Assets/Blocks/source/generate-textures.mjs
node Tools/check-block-assets.mjs
node --test Tools/check-block-assets.test.mjs
```

检查器读取描述、贴图、来源与官方方块目录；核对尺寸一致、透明度类别、引用可达和许可记录。失败时修对应源和描述，再重新生成。

## 导出设置与来源

Sample 整包边长是 128，贴图采用最近邻采样。自绘源中的小像素图由脚本放大，不能仅替换一个尺寸不同的 PNG。镂空与半透明应在真实视图核对，见 [世界资产](world-assets.md)。

来源记录应包含作者、来源页、版本、许可、修改和原图哈希。Sample 检查器接受 CC0-1.0 与 CC-BY-4.0；后者要在 `ATTRIBUTION.md` 署名。其它项目使用什么许可由项目决定，不能把本插件的 MIT 当作图片许可。采购凭据等私密材料留在项目受控位置。

## UI、图标与其它资产

优先沿用项目已有消费入口，记录显示尺寸、透明度、缩放和适用状态。先做一件，在实际大小与深浅背景检查，再扩量。源文件、预览与运行文件分别保存，命名变化后更新真实消费者。

通用模型或图集导入在示例中尚未提供；先确认目标客户端的入口，不能用一个人工清单冒充引擎配置。制作目标见 [简报与风格](brief-and-style.md)。

## 交回内容

交回可修改源、运行文件、来源记录、导出命令、检查器结果和真实页面截图。标明哪些步骤执行过、哪些仍待检查，接入操作见 [接入与验收](integration-and-review.md)。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
