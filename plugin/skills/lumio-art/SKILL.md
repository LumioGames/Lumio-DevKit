---
name: lumio-art
description: 为 Lumio 游戏制定美术简报、制作和交接 UI、图标、方块材质与实体表现，沿 Sample 资源流程导入并在 WebGL2 客户端验收。不替代玩法实现或未提供的通用模型导入器。
---

# Lumio 美术制作与接入

把玩家需要辨认的内容做成可修改、有来源、能在客户端显示的资产，沿用项目已有画风与工具。

| 任务 | 阅读 |
| --- | --- |
| 明确用途与风格，先做代表样品 | [简报与风格](references/brief-and-style.md) |
| 管理源、导出、来源和交接 | [资产生产](references/asset-production.md) |
| 方块描述、材质与世界对象分工 | [世界资产](references/world-assets.md) |
| 接入 WebGL2 页面、排查显示并验收 | [接入与验收](references/integration-and-review.md) |

先确认使用场景和消费入口，再制作一件并放进真实画面；验证导出设置后扩量。修改生成资产时改源并重新导出，保留来源与许可记录。

世界只有方块与实体；资源决定外观，玩法决定碰撞、伤害、库存与同步。通用模型导入在示例中尚未提供，按项目实际入口对接。视觉检查和客户端接入分别交回结果。

核对基线：LumioSample@f98322c2eec8f83b5caf07aa2ad15d9c55b6f8fb · Engine v0.0.2 · 2026-09-27 · 验证范围（静态核对）
