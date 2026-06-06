<div align="center">

# ⌨️ KeyType

### Windows 键盘输入工具 — 模拟逐字键入，绕过粘贴限制

---

</div>

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows-0078D4?style=flat-square&logo=windows&logoColor=white)
![Version](https://img.shields.io/badge/version-1.0.0-green?style=flat-square)

</div>

<div align="center">

[中文](#中文) | [English](#english)

</div>

---

## 中文

### 🎯 这是什么

一个轻量级的 **Windows** Python 小工具，通过模拟键盘逐字输入，可以在 **禁止粘贴** 的平台（头歌、学习通、部分在线考试系统等）中输入内容。

### ✨ 功能特性

- 🖱️ **点击指定坐标** — 自动点击屏幕任意位置
- ⌨️ **模拟键盘输入** — 逐字键入，支持中文、Emoji 等 Unicode 字符
- 📋 **剪贴板读取** — 从剪贴板读取内容并自动输入
- 📍 **鼠标坐标查看** — 实时显示当前鼠标位置
- 🚫 **绕过粘贴限制** — 对系统而言与真人打字完全一致

### 📦 快速开始

```bash
# 克隆项目
git clone https://github.com/your-username/your-repo.git
cd your-repo

# 直接运行（双击 .py 文件或命令行）
python type_to_position.py
```

### 🚀 使用方式

**交互菜单**（双击运行）：

```text
1：输入指定文本到指定坐标
2：从剪贴板输入到指定坐标
3：查看当前鼠标坐标
0：退出
```

**命令行参数**：

```bash
# 输入文本到指定坐标
python type_to_position.py "你好" 500 300

# 从剪贴板输入
python type_to_position.py --clipboard 500 300

# 仅查看鼠标坐标
python type_to_position.py --show-mouse

# 只输入，不点击
python type_to_position.py --no-click "测试" 400 250
```

### 📖 推荐流程

```text
1. 选择 3 → 查看鼠标坐标
2. 移动鼠标到目标输入框 → 按 Enter 保存坐标
3. 选择 1 或 2 → 自动复用坐标，一键输入
```

### 🛠️ 技术实现

| 功能 | 实现方式 |
|------|----------|
| 鼠标移动/点击 | `user32.SetCursorPos` + `SendInput` |
| 键盘输入 | `user32.SendInput`（`KEYEVENTF_UNICODE`） |
| 剪贴板读取 | `OpenClipboard` → `GetClipboardData` |
| 控制台窗口 | `SetConsoleScreenBufferSize` |

> 纯标准库实现，无需安装任何第三方依赖！

---

## English

### 🎯 What is this

A lightweight **Windows** Python tool that simulates keyboard typing character-by-character, allowing you to input text on platforms that **block paste operations** (e.g., educational websites, online exam systems).

### ✨ Features

- 🖱️ Click at any screen coordinate
- ⌨️ Simulate keyboard input with full Unicode support (Chinese, Emoji, etc.)
- 📋 Read from clipboard and auto-type
- 📍 Real-time mouse coordinate viewer
- 🚫 Bypass paste restrictions — identical to real typing

### 🚀 Quick Start

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
python type_to_position.py
```

### 📖 Command Line

```bash
python type_to_position.py "Hello" 500 300        # type text
python type_to_position.py --clipboard 500 300     # from clipboard
python type_to_position.py --show-mouse             # show coordinates
python type_to_position.py --no-click "Test" 400 250  # type without clicking
```

---

<div align="center">

**Made with ❤️ by [Your Name]**

</div>
