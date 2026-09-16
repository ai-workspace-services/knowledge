# 07 / 10｜状态管理之前，先问：这份数据是谁的？

## 微信 / 朋友圈

**标题：** 状态管理之前，先问：这份数据是谁的？

状态管理最容易犯的错误：

**所有东西都往一个 Store 塞。**

其实决定 State 放哪里的关键，是先判断：

**谁拥有这份数据？**

UI State → 页面/组件  
Props → 父组件  
Server State → 后端/API  
Database → 持久化事实

Hooks 本身也不是数据库，更不自动拥有数据。

所以 State Management 的第一原则：

> **先分清数据主人，再决定谁来管理。**

## 小红书

**标题：**

> Zustand、Redux、React Query 之前，先回答一个问题

这份数据：

**到底是谁的？**

我觉得这是状态管理最重要的一道题。

如果只是：弹窗开关、Tab、Hover、输入框

→ UI State

如果是父组件传给子组件：

→ Props

如果来自 API：用户、订单、通知、统计数据

→ Server State

如果是系统长期存在的真实业务数据：账户、账单、配置、订单

→ Database / Source of Truth

很多前端项目状态管理失控，并不是“缺一个更好的状态库”。

而是：

**把完全不同生命周期、不同所有权的数据塞进了同一个 Store。**

## X

**Title:** State management starts with data ownership.

Before choosing Redux, Zustand or React Query, ask:

**Who owns this data?**

UI State → component/page  
Props → parent  
Server State → API/backend  
Persistent truth → database

Most state-management problems are ownership problems before they are library problems.

07/10

## LinkedIn

**Title:** Most state-management problems are ownership problems.

Before selecting a state-management library, clarify data ownership.

A useful separation:

**UI state** — temporary and local.

**Props** — owned by the parent.

**Server state** — synchronized with a remote service.

**Database state** — durable source of truth.

Once ownership and lifecycle are explicit, the implementation choice becomes much easier.

State management is often a boundary problem disguised as a library problem.
