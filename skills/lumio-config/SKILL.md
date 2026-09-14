---
name: lumio-config
description: 为 Lumio 游戏编辑 Schema 与配表，用 LumioConfig 校验、名字补丁、导出及生成 C# Reader，并接入运行时读取、客户端/服务器可见性与配置更新验证；不用于实现配置编译器或自动激活生产配置。
---

# Lumio 游戏配表

把玩法数值从权威表源编译成按端隔离的产物，在装载时构建 typed Reader，游戏帧内读取一致的数据。按任务只读必要参考。

## 任务路由

| 用户要做什么 | 阅读 |
| --- | --- |
| 改数值、新列/新表、默认值、引用、行号、S/C/V 可见性 | [表源与 Schema](references/source-and-schema.md) |
| 校验、名字补丁、导出 JSON、生成 Reader、复制到游戏 | [编辑与导出](references/edit-and-export.md) |
| 游戏读取、缺表诊断、启动装载、重启更新或 Tick 切换 | [运行时读取与更新](references/runtime-and-updates.md) |

SDK 和项目公共说明见 [运行时前置](references/runtime-and-updates.md#运行时前置)。LumioConfig CLI 本身只需 Python 3.11 以上，不依赖私有引擎源码。

## 执行方式

1. 找到游戏真正消费的导出根、目标端和表；查 Schema 后再改值。
2. 区分数值改动与 Schema 改动：前者通常只改变数据产物，后者还要重建 Reader 和重新编译消费方。
3. 通过名字补丁修改行，校验、导出到新的输出目录，核对产物与端可见性。
4. 用运行时 Reader 证明新值被读取；涉及真实游戏更新时再确认 Host 实际装载的 Revision 与行为。

## 关键约束

- `tables/`、`schemas/`、`registry/` 是源；导出 JSON 和 Reader 是生成物，不手改来绕过校验。
- 表只保存数据，不放脚本、条件执行或业务状态。行号是稳定身份，删除进入墓碑，不自行复用。
- 未声明 `visibility` 的列默认只有服务器可见；客户端隔离必须发生在产物内容与分发目录，不能只靠 UI 隐藏。
- 生成的 C# 只有类型和读法，没有行数值。玩法不在每帧读文件、解析 JSON 或用零值掩盖必填配置错误。
- `export` 不等于运行时已加载；Sample 默认缓存首次装载结果，改文件后通常要重启。
- 示例和工具事实核对于 2026-09-14；接口、缓存行为及分发能力以当前 SDK/Host 为准，不承诺自动热更。
- 生产激活不属于本技能的自动操作；交付数据和验证结果，由项目的生产发布流程决定上线。
