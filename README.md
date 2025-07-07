# LiveReloadPy

> 💡 Sublime Text 插件 — 专为前端开发者优化的 LiveReload 解决方案

LiveReloadPy 是一款为 HTML/CSS/JS 前端开发者量身打造的 Sublime Text 插件，集成 `livereload` 库，提供高效的开发工作流，支持**整个项目监视**和**单独文件监视**两种模式，满足不同开发场景需求。

---

<details>
<summary><kbd>目录树</kbd></summary>

#### TOC
- [✨ 核心特性](#-核心特性)
- [🧩 安装指南](#-安装指南)
- [⚙️ 配置系统](#-配置系统)
- [🚀 核心命令](#-核心命令)
- [🔧 使用场景](#-使用场景)
- [❓ 常见问题解答](#-常见问题解答)
- [🛠 兼容性](#-兼容性)
- [📄 开源协议](#-开源协议)
</details>


## ✨ 核心特性

- ⚡ **纯 Python 实现** - 基于 Python `livereload` 库，无需 Node.js
- 🧠 **智能文件监视，双模式监视支持**
  - **项目级监视**：自动递归监听项目目录中的 HTML/CSS/JS/Vue 等文件变更
  - **文件级监视**：单独监听当前编辑文件
- 🌐 **一键预览** - 在浏览器打开当前文件的 Live 地址
- 📦 **多级配置系统** - 全局设置 + 项目级配置（`.livereload.json`）
- 🚀 **性能优化** - 支持忽略目录（如 node_modules, .git）
- 🛠 **状态实时反馈** - 状态栏显示服务器状态 + 文件保存提示
- ⚙️ **高度可配置** - 端口、自动打开浏览器、监视扩展名、调试模式等
<!--- 📦 支持 Sublime Text 的命令面板、右键菜单、顶部菜单-->

---

## 🧩 安装指南

### Package Control（推荐）

1. `Ctrl+Shift+P` → `Package Control: Add Repository`
2. 输入仓库地址：`https://github.com/maboloshi/LiveReloadPy`
3. `Ctrl+Shift+P` → `Package Control: Install Package`
4. 搜索 `LiveReloadPy` → 安装

<!--尚未发布，计划提交到 [Package Control Channel](https://github.com/wbond/package_control_channel)。-->

### 手动安装

1. 克隆仓库到 Packages 目录：
   ```bash
   git clone https://github.com/maboloshi/LiveReloadPy.git
   ```
1. 重启 Sublime Text

---

## ⚙️ 配置系统

### 全局配置

通过以下方式打开插件配置：

- 命令面板输入 `LiveReloadPy: ⚙ 打开插件设置`
- `Preferences > Package Settings > LiveReloadPy > Settings`
- `Tools > LiveReloadPy > ⚙ 打开 LiveReloadPy 设置`

```json
{
  "port": 5500,
  "open_browser_on_start": false,
  "watch_extensions": [".html", ".css", ".js", ".vue"],
  "ignore_dirs": [".git", "node_modules", "dist"],
  "debug_mode": false
}
```

### 项目级配置（优先）

在项目根目录创建 `.livereload.json` 文件：

```json
{
  "port": 8080,
  "watch_extensions": [".html", ".js", ".css", ".scss"],
  "ignore_dirs": ["temp", "build"]
}
```

---

## 🚀 核心命令

| 命令名称（命令面板） | 说明 | 快捷键建议 |
|-------------------|------|------------|
| `LiveReload: ▶ 启动服务器` | 启动 livereload 监听服务 | `Ctrl+Alt+L` |
| `LiveReload: ⏹ 停止服务器` | 停止 livereload 服务 | `Ctrl+Alt+K` |
| `LiveReload: 🌐 打开当前文件` | 在浏览器打开当前文件预览 | `Ctrl+Alt+O` |
| `LiveReload: 👁️ 添加单独监视` | 单独监视当前文件 | `Ctrl+Alt+W` |
| `LiveReload: ⚙ 打开插件设置` | 修改全局配置 | - |

---

## 🔧 使用场景

### 基础工作流
1. 打开项目文件夹
2. `Ctrl+Shift+P` → `LiveReload: ▶ 启动服务器`
3. 编辑 HTML/CSS/JS 文件
4. 保存文件 → 浏览器自动刷新！

### 快速预览
1. 打开要预览的文件
2. `Ctrl+Shift+P` → `LiveReload: 🌐 打开当前文件`
3. 或使用右键菜单中的选项

### 项目特定配置
1. 在项目根目录创建 `.livereload.json`
2. 自定义端口、监视文件类型等
3. 重启服务器应用新配置

---

## ❓ 常见问题解答

### Q1: 修改项目中的 HTML 文件时，所有打开的页面都会刷新吗？

✅ **是的，所有通过 LiveReload 连接的页面都会自动刷新**

#### 工作原理：
1. 每个打开的页面都会与 LiveReload 服务器建立 WebSocket 连接
2. 当服务器检测到文件变更时：
   - 向所有连接的客户端发送刷新指令
   - 每个页面独立刷新自己

#### 刷新范围：
| 修改的文件类型 | 刷新行为 |
|----------------|----------|
| HTML 文件 (如 `index.html`) | 所有打开该文件的页面刷新 |
| CSS 文件 (如 `styles.css`) | 所有使用该 CSS 的页面刷新 |
| JS 文件 (如 `script.js`) | 所有使用该 JS 的页面刷新 |

### Q2: 为什么需要全局刷新？这不是会干扰其他页面吗？

💡 **全局刷新是设计优势而非缺陷**：
1. **效率提升**：同时开发多个页面时，所有相关视图实时更新
2. **一致性保证**：确保修改 CSS/JS 后所有页面状态同步更新
3. **响应式测试**：多设备预览时，所有设备视图同步刷新

#### 实际场景：
- 设计师同时查看桌面/移动端视图
- 开发者测试组件在多个页面的表现
- 修改全局样式时查看整体效果

### Q3: 如何避免全局刷新影响工作？

🛡 **解决方案**：
1. **使用单独监视模式**：
   ```python
   # 只监视特定文件
   LiveServerController.add_single_file_watch("about.html")
   ```
2. **浏览器端控制**：
   ```javascript
   // 自定义刷新逻辑（需在前端代码中添加）
   livereload.listen({
     onRefresh: function(path) {
       if (path.includes("header.css")) {
         // 只刷新页眉组件
         document.getElementById("header").reload();
       } else {
         location.reload();
       }
     }
   });
   ```
3. **开发策略**：
   - 使用无痕模式窗口开发关键页面
   - 将测试页面分组到不同浏览器窗口
   - 重要表单数据在修改前先保存

### Q4: 刷新会导致页面状态丢失吗？

⚠️ **是的，刷新会重置页面状态**：
- 未提交的表单数据会丢失
- 页面滚动位置重置
- 打开的弹窗/模态框关闭

#### 缓解方案：
1. 使用 Vue/React 等框架的本地状态管理
2. 开发时避免在关键表单中操作
3. 利用浏览器开发者工具的"Preserve log"功能

### Q5: 支持单页面应用(SPA)吗？

✅ **完全支持**：
- 修改 HTML 会刷新整个 SPA
- 当前路由状态通常保持（取决于 SPA 路由实现）
- 建议配合 Vue/React 热更新使用效果更佳

> 💡 提示：对于复杂 SPA 项目，推荐使用 `add_single_file_watch` 精准控制刷新范围

---

## 🛠 兼容性

* ✅ **Sublime Text 4** (Build 4000+)
* ✅ **全平台支持** - Windows / macOS / Linux


## 📄 开源协议

MIT License - 自由使用和修改
