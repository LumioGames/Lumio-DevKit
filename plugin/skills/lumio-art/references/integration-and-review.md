# 客户端接入、显示排障与验收

验收要确认目标客户端实际加载了这批资产，并且玩家能正确辨认。

## 方块资产接入流程

1. 按 [资产生产](asset-production.md) 修改并运行 `node Tools/check-block-assets.mjs`。
2. 按 [客户端搭建](../../lumio-client/references/setup.md) 构建客户端、Bot 和浏览器玩法，发布 spectator，再用该页带场景 DLL 和 `--spectator` 的完整命令启动。
3. 打开启动器打印的 HTTP 地址，加 `?view=blocks` 进入 WebGL2 三维方块视图。
4. 在浏览器 Network 检查 `game-assets/Blocks/` 下的描述、`pack.json` 与贴图；在 Console 检查资源错误。
5. 对照 `Client/Assets/Blocks/preview/blocks-preview.png`，检查顶、侧、底、交叉面片，确认透明和镂空类别表现正确。
6. 保存资产版本、检查器结果、页面地址、截图和剩余问题。

这条发布路径来自 [Client/UI/Spectator/host/Lumio.Sample.Client.Spectator.csproj](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Client/UI/Spectator/host/Lumio.Sample.Client.Spectator.csproj)。实际发布目录是 `Client/UI/Spectator/host/bin/Release/net10.0/publish/wwwroot`；源目录不包含完整运行文件。

## 显示排障

| 现象 | 检查 | 下一步 |
| --- | --- | --- |
| 只有俯视图 | URL 的 `view` 参数 | 使用 `?view=blocks`。 |
| 方块变紫黑格 | 缺失贴图和资产警告 | 修引用与发布文件，再发布。 |
| 仍是旧素材 | 实际响应内容、发布目录和浏览器缓存 | 确认重新发布的版本被加载。 |
| 透明或镂空错误 | PNG alpha、材质类别和相邻面 | 与 Sample 同类资源比较。 |
| 空白页面 | `_framework/`、WASM、模块映射和 HTTP 状态 | 按 [客户端排障](../../lumio-client/references/diagnostics.md) 处理。 |
| 替换后变慢 | 相同场景的帧耗时与资源数量 | 测量后调整尺寸或数量。 |

先用普通 Sample 地图确认接入；要观察湖边场景，按 [Spectator README](https://github.com/LumioGames/LumioSample/blob/f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb/Client/UI/Spectator/README.md) 选择 `Server/Config/Startup/server.acceptance.json`，不要误把普通地图未出现的方块判成资源损坏。

## 交接

视觉检查与客户端接入分别写结果。资源检查通过后仍要看真实画面；没有执行浏览器检查就记为“未执行”，列出待检查场景。帧耗时需要实测，文件体积不能代替性能结论。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
