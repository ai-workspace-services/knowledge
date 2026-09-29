# 09 / 10｜AI 生成依赖之后，项目为什么还能稳定运行？

## 微信 / 朋友圈

AI 可以一分钟生成一个 Node.js 项目，也可以顺手加入几十个依赖。

但项目能不能在另一台机器、另一个 CI 环境、下一次部署中稳定运行，取决于你是否理解这条依赖供应链：

**package.json  
→ lockfile  
→ npm / pnpm  
→ node_modules  
→ build  
→ test  
→ deploy**

这几个东西不是一回事：

- **package.json**：项目声明“我想要什么”。
- **lockfile**：记录“最终解析成了哪些精确版本”。
- **npm / pnpm**：根据规则解析并安装依赖。
- **node_modules**：当前机器实际安装出的物料。
- **build artifact**：最终进入测试、部署和运行环境的产物。

所以：

**package.json ≠ lockfile ≠ node_modules ≠ build artifact**

### 让 AI 生成项目依赖时，先给 5 个约束

1. Node.js 和包管理器的版本。
2. 使用 npm、pnpm 还是其他包管理器。
3. lockfile 是否必须提交并参与 CI。
4. 哪些依赖是运行时依赖，哪些只是开发依赖。
5. 构建、测试和部署需要生成什么可验证产物。

## 如何排查“我电脑能跑，CI 却失败”？

按供应链顺序检查：

1. **版本**：Node、npm/pnpm、操作系统是否一致？
2. **清单**：package.json 的 scripts、依赖范围和 workspace 配置是否正确？
3. **锁定**：lockfile 是否提交、是否与 package.json 同步？
4. **安装**：是否使用了与 lockfile 匹配的 frozen/immutable 安装模式？
5. **构建**：依赖是否只在本地存在，或被错误放在 devDependencies？
6. **安全**：依赖来源、许可证、漏洞和安装脚本是否可信？

AI 越能自动生成依赖，越需要人来验证依赖来源、版本变化和构建结果。

> **工程化真正关心的不是“能安装”，而是可复现、可信、可追溯。**

## 小红书

**标题：**

> AI 生成几十个依赖后，怎么保证项目不是“我电脑能跑”？

第一次接触 Node.js 项目时，很多人会觉得：

```bash
npm install
npm run dev
```

像魔法。

但 AI Coding 时代，真正需要理解的是：

**依赖不是安装完就结束，而是一条供应链。**

```text
package.json
→ lockfile
→ npm / pnpm
→ node_modules
→ build
→ test
→ deploy
```

### 4 个文件/阶段分别代表什么？

**package.json**：项目想要什么。

**lockfile**：最终精确解析出了什么。

**node_modules**：当前机器实际装出了什么。

**build artifact**：最后交付出去的是什么。

所以：

```text
package.json ≠ lockfile ≠ node_modules ≠ build artifact
```

### 让 AI 加依赖前，先问这些问题

1. Node 和 pnpm/npm 版本是什么？
2. 这个依赖是运行时需要，还是开发时需要？
3. lockfile 是否要提交？
4. CI 是否会使用 frozen install？
5. 依赖的来源、许可证和漏洞谁来检查？

### CI 失败怎么查？

1. 本地和 CI 的 Node/包管理器版本一致吗？
2. package.json 和 lockfile 是否同步？
3. 是否错误地依赖了本地缓存或未提交文件？
4. 运行时依赖是否被放进了 devDependencies？
5. 构建产物是否真的包含了需要的依赖？

AI 可以更快地生成依赖，但不能替你保证依赖供应链可信。

## X

**Title:** AI-generated dependencies need a reproducible supply chain.

`npm install` is not magic. It materializes a dependency graph:

package.json → lockfile → package manager → node_modules → build artifact

These are different layers:

package.json → declared intent  
lockfile → resolved versions  
node_modules → local materialization  
build artifact → deployable output

Before asking AI to add a dependency, define:

1. Node and package-manager versions.
2. Runtime vs development dependency rules.
3. Lockfile and immutable-install policy.
4. Build and test requirements.
5. Dependency provenance, licenses, and security checks.

When “works on my machine” returns, debug:

1. Versions.
2. Manifest and scripts.
3. Lockfile consistency.
4. Clean installation.
5. Runtime dependency classification.
6. Build artifact contents.

**AI accelerates dependency creation. Engineering controls make it reproducible.**

09/10

## LinkedIn

**Title:** AI-assisted development makes dependency provenance a first-class concern

AI can generate an application and its dependency list quickly. That increases the importance of understanding the dependency supply chain rather than treating package installation as a local convenience.

A useful model is:

**package.json → lockfile → package manager → installed tree → build artifact**

Each layer answers a different question:

- **package.json** expresses project intent.
- **lockfile** records the resolved dependency graph.
- **Package manager** applies resolution and installation rules.
- **Installed tree** is the materialized environment.
- **Build artifact** is what tests and deployment should validate.

When asking AI to modify dependencies, define the controls up front:

1. Supported Node.js and package-manager versions.
2. Runtime and development dependency boundaries.
3. Lockfile ownership and immutable installation policy.
4. Reproducible build and test commands.
5. Provenance, license, vulnerability and install-script review.

When local development succeeds but CI fails, compare the supply chain in order: versions, manifest, lockfile, clean install, dependency classification, and final artifact.

The broader lesson is:

> **AI can create dependencies faster than teams can review them. Reproducibility, provenance and dependency hygiene must therefore be designed into the workflow.**

