# 游戏代码写法（TypeScript 引擎）

目标：写游戏代码前选对写法，计时器、缓存、事件流和重试用引擎已有的通用库，不手写第二份；模拟代码保持可存档、可回放、多端一致。

## 适用范围

本篇适用于用 TypeScript 引擎 `lumio-engine` 写的游戏（通用库入口 `lumio-engine/runtime`，游戏仓按提交号固定引擎）。核对于 2026-11-01，对照引擎主干提交 `1869dcd53e85bedf4535dfc6c88c840a50e77270`；权威文字在引擎仓 `.spec/knowledge/standards/code-style.md` 与 `.spec/knowledge/features/runtime-core.md`「通用库」，同步引擎后也在游戏仓的 `.engine/` 里。不能访问引擎仓时，以本篇要点为准，缺口向引擎维护方确认，不自己补一份通用实现。

本手册其余篇章讲的 .NET SDK 项目不在本篇范围：那里同一个原则是用 SDK 对应 facade，不在玩法层另造计时、状态机、空间查询或预测算法（见[能力与证据范围](capabilities.md)）。

## 先判断「出来几个值」

| 要写的东西 | 用 | 来自 |
| --- | --- | --- |
| 一个结果（加载、请求、握手） | 普通 `async / await`，由所属对象的作用域守住：`await scope.wait(…)`；超时 `withTimeout(…, { signal: scope.signal })`；重试 `retry` / `backoffDelay`；不等结果的用 `scope.run(…)` | `lumio-engine/runtime` |
| 一串事件（点击、输入、消息、轮询结果） | RxJS 7.8.2，唯一的链式写法；管道末尾 `named('名字')` 再 `untilDisposed(scope)` | 运算符来自 `rxjs`，接引擎的桥来自 `lumio-engine/runtime` |
| 有状态的流程（连接、房间、对局阶段） | 分层状态机 `createHfsm` | `lumio-engine/runtime` |
| 分支 | 普通 `if / else`、`switch` | 语言本身 |
| 游戏规则里的「N 秒后」「每 N 秒」 | `TickSchedule`：`tickAfter`、`tickEvery`、`tickDue`；毫秒先按逻辑帧率换算成整数帧 | `lumio-engine/runtime` |

不要把一次请求包成 Observable 再取第一个值；不要在管道里堆条件回调；不要吞掉失败。

## 谁创建谁销毁

开始计时器、订阅、监听、Worker 或 `await` 的那个类持有一个 `Scope`，由它自己的 `dispose()` 全部结束。不在一处创建、另一处销毁，也不让别人替它清理。每个界面、房间、连接从上一级 `scope.child()` 一个，只结束自己的那一层。

下面是原创示例，用 `lumio-engine/runtime` 的名字（`Scope`、`Emitter`、`fromEmitter`、`named`、`untilDisposed`、`withTimeout`、`LruCache`），两段示例都用上述提交的类型定义做过类型检查，并在带占位函数的独立脚本里运行过（面板销毁后，未完成的 `open` 不再显示；调度示例的引信在预期帧触发一次），没有在真实游戏里运行：

```ts
import { map } from 'rxjs';
import { Emitter, LruCache, Scope, fromEmitter, named, untilDisposed, withTimeout } from 'lumio-engine/runtime';

interface Profile {
  readonly id: string;
}
declare function loadProfile(id: string, options: { signal: AbortSignal }): Promise<Profile>;
declare function showProfile(profile: Profile): void;

class ProfilePanel {
  readonly scope: Scope;
  private readonly cache = new LruCache<string, Profile>({ maxEntries: 64 });

  constructor(parent: Scope, clicks: Emitter<[string]>) {
    this.scope = parent.child('ProfilePanel');
    // 一串事件：管道有名字，面板关掉流就结束
    fromEmitter(clicks)
      .pipe(map(([id]) => id), named('profileClick'), untilDisposed(this.scope))
      .subscribe((id) => void this.scope.run(() => this.open(id)));
    // 定时同样挂在作用域上
    this.scope.timers.every(30_000, () => this.cache.clear(), { label: 'profileCacheReset' });
  }

  // 一个结果：面板关了之后 wait 以 CancelledError 结束，下面的 show 不会执行；不等结果的调用方用 scope.run，取消不算失败
  async open(id: string): Promise<void> {
    const profile =
      this.cache.get(id) ?? (await this.scope.wait((signal) => withTimeout(loadProfile(id, { signal }), 3000, { signal })));
    this.cache.set(id, profile);
    showProfile(profile);
  }

  dispose(): void {
    this.scope.dispose();
  }
}
```

预期：面板销毁后，它的定时、订阅和等待中的 `open` 一起结束；缓存满了先淘汰最久没用的键。失败定位：RxJS 管道出错会得到带管道名的 `FlowError`（`cause` 是原错误）；作用域结束得到 `CancelledError`，`scope.run` 把它当正常结束。

## 模拟代码

各游戏的 `gameplay/`（系统、规则、Bot、地图生成，以及客户端要预测或回放要重算的任何结果）只用 `TickSchedule`、`det*` 三角（`detSin`、`detCos`、`detAtan2`）、`ipow` 和 `rng*`。不得用 RxJS、`async / await`、`setTimeout`、`Date.now`、`Math.random`，也不得用 `Math` 的三角、指数、对数、幂和 `hypot`：它们存不进世界，或在不同 JS 引擎上结果可能差一位。渲染、音效、界面可以用 `Math`。

```ts
import { tickAfter, tickDue, type TickSchedule } from 'lumio-engine/runtime';

// 计划是存进组件的纯数据；每帧 tickDue 后按 id 执行对应动作。引信时长先换算成整数帧再传入
function armFuse(schedule: TickSchedule, tick: number, fuseTicks: number): TickSchedule {
  return tickAfter(schedule, 'bomb-fuse', tick, fuseTicks);
}
function stepFuse(schedule: TickSchedule, tick: number, explode: () => void): TickSchedule {
  const { fired, schedule: next } = tickDue(schedule, tick);
  for (const timer of fired) if (timer.id === 'bomb-fuse') explode();
  return next;
}
```

## 不手写通用库的副本

| 需要 | 用 |
| --- | --- |
| 有上限的缓存、「最近 N 条」 | `LruCache`、`RingBuffer`（不要手写「满了删最早的键」） |
| 监听者列表 | `Emitter`（不要手写 `Set<回调>`） |
| 最多等 N 毫秒、等待 | `withTimeout`、`sleep`（不要手写 `Promise.race` 和计时器） |
| 重试与退避 | `retry`、`backoffDelay`（不要手写 `2 **` 指数） |
| 数值、角度、向量 | `clamp`、`lerp`、`smoothstep`、`wrapAngle`、`angleDifference`、`TAU`、`Vec2` |
| 缓动 | `Easing`（只用于表现） |
| 格子寻路、距离场 | `gridAStar`、`gridDistances` |
| 随机抽取、哈希 | `rngShuffle`、`rngPick`、`fnv1a32` |

引擎不提供补间：界面与特效动画是游戏自己的表现逻辑，留在游戏里，缓动曲线用 `Easing`。

## 怎么检查

游戏仓的 `npm run check` 在类型检查和引擎入口导入检查之后运行通用库检查，它用 `lumio-engine/testing` 的 `checkSharedLibrary` 报出手写副本、模拟目录里的不确定计算与 RxJS、没有主人的 RxJS 订阅，以及与引擎不同的 `rxjs` 版本。`package.json` 里 `rxjs` 精确写 `7.8.2`（不带 `^` 或 `~`）。必须保留原写法的那一行写 `shared-library-allow: 理由`（同一行或上一行）；这个标记要写明原因，不用来绕过检查。

游戏以后可能经 PuerTS 在 Unity 里运行：共享游戏逻辑不新增只有浏览器才有的 API。这是约束，不代表现在已做兼容验证。
