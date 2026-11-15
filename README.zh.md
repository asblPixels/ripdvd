<div align="center">

<img src="data/logo.png" width="150" alt="RipDvD logo">

# 🎬 RipDvD

### 从光盘到数字 — 轻松无忧。

**面向 Linux (Fedora / GNOME) 的极简开源 DVD 提取工具**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%26%20Windows-blue.svg)](https://github.com/asblPixels/ripdvd)
[![Desktop](https://img.shields.io/badge/desktop-GNOME%2049-green.svg)](https://gnome.org/)
[![GUI](https://img.shields.io/badge/GUI-GTK4%20%2F%20libadwaita-teal.svg)](https://gnome.org/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Backend](https://img.shields.io/badge/backend-HandBrakeCLI-orange.svg)](https://handbrake.fr/)
[![CI](https://github.com/asblPixels/ripdvd/actions/workflows/ci.yml/badge.svg)](https://github.com/asblPixels/ripdvd/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/asblPixels/ripdvd.svg)](https://github.com/asblPixels/ripdvd/releases)

<br>

[🇬🇧 English](README.md) · [🇫🇷 Français](README.fr.md) · [🇪🇸 Español](README.es.md) · [🇷🇺 Русский](README.ru.md) · [🇨🇳 中文](README.zh.md) · [🇯🇵 日本語](README.ja.md)

</div>

---

## 📖 关于

**RipDvD** 是一款免费、开源的 Linux 和 Windows DVD 提取应用程序。
它在 [HandBrakeCLI](https://handbrake.fr/) 之上提供原生图形界面（Linux 上为 GTK4 / libadwaita，Windows 上为 tkinter），
将您的 DVD 收藏转换为高质量的 MKV 文件，适用于家庭媒体服务器（Jellyfin、Kodi、Plex）。

> **起源**：本项目由 **[asblPixels](https://github.com/asblPixels)** 创建并维护，
> 作为其开源软件计划的一部分。采用 MIT 许可证发布，
> 可自由使用、修改和分发。

### ✨ 为什么选择 RipDvD？

大多数 DVD 提取工具要么仅支持命令行，要么过于复杂，要么仅限于特定平台，要么仅限 Windows。
RipDvD 的目标是成为 **在任何地方都能工作的最简单工具**：插入光盘，点击一个按钮，获得完美的 MKV。
无需配置，但需要时提供完全控制。
支持 **Fedora、Arch、Ubuntu、Debian** (Linux) 和 **Windows 10/11**。

## 🎯 功能

- 🖱️ **一键提取** — 插入 DVD，点击 *Rip DVD*，获得可直接串流的 MKV。
- 🔍 **自动检测主标题** — 自动选择最长的标题（主电影）。
- 🌍 **多语言音频** — 检测所有音轨；默认优先法语，然后英语。
- 💬 **字幕** — 可选透传任何字幕轨道（VobSub），或不包含。
- 📑 **章节标记** — 保留在 MKV 中，便于在 Jellyfin/Kodi 中导航。
- 📺 **实时输出窗口** — HandBrakeCLI 实时日志，自动滚动。
- 📊 **进度条** — 编码过程中实时更新百分比。
- ⏸️ **停止按钮** — 随时取消正在进行的编码。
- 🔄 **恢复按钮** — 使用相同参数重试上次编码。
- 🚪 **退出按钮** — 干净地关闭应用程序（先停止任何正在运行的编码）。
- 🔄 **重新扫描按钮** — 无需重启应用程序即可重新分析光盘。
- 🧹 **清除日志** — 清除实时输出窗口。
- 🎨 **原生 GNOME 外观** — GTK4 + libadwaita，完美融入 Fedora Workstation。
- 🧵 **线程安全** — 所有界面更新都编组到 GTK 主线程。
- 🐛 **调试日志** — 完整输出保存到 `~/.ripdvd-debug.log`。

## 📋 默认输出配置

| 参数 | 值 |
|---|---|
| 容器 | MKV (Matroska) |
| 视频编解码器 | H.264 (x264), RF 20, 预设 `medium` |
| 分辨率 | DVD 原生 (480p NTSC / 576p PAL) — 无升频 |
| 帧率 | 源 (25 / 29.97 fps) |
| 音频 | 透传 (复制) — 保留原始 5.1（如果存在） |
| 字幕 | 透传 (可选) |
| 章节 | 保留 |
| 典型大小 | ~1.0 – 1.5 GB / 2 小时电影 |

> 💡 DVD 是 SD 源。保持原生分辨率可避免人为升频，
> 保持文件小巧，同时在任何电视上看起来都很棒。

## 🖥️ 支持的系统

| 组件 | 要求 |
|---|---|
| **操作系统** | Fedora 43+ (在 Fedora 45 上测试)。任何基于 Fedora/RHEL 的近期发行版都应该可以工作。 |
| **桌面环境** | GNOME (GTK4/libadwaita)。支持 X11 和 Wayland。 |
| **架构** | x86_64 |
| **CPU** | 任何 x86_64 (通过 x264 软件编码)。无需 GPU。 |
| **内存** | 最低 2 GB，推荐 4 GB |
| **磁盘** | 每部电影 ~1.5 GB 可用空间 (输出) + 编码期间 ~8 GB 临时空间 |
| **光驱** | 内置或 USB DVD 读取器 (显示为 `/dev/sr0`) |

### 支持的发行版

本仓库为每个发行版提供分支，包含适配的安装程序：

| 分支 | 发行版 | 安装脚本 |
|---|---|---|
| `main` / `fedora` | Fedora 43+ | `scripts/install.sh` |
| `arch` | Arch Linux | `scripts/install-arch.sh` |
| `ubuntu` | Ubuntu 22.04+ | `scripts/install-ubuntu.sh` |
| `debian` | Debian 12+ | `scripts/install-debian.sh` |
| `windows` | Windows 10/11 | `scripts/install-windows.ps1` |

使用特定分支：

```bash
git clone -b <分支> https://github.com/asblPixels/ripdvd.git
cd ripdvd
bash scripts/install-<distro>.sh   # 或 Windows 上使用 .ps1
```

## 🚀 安装

### ⚡ 一行安装（推荐）

**将这一行命令复制粘贴到终端：**

```bash
curl -fsSL https://raw.githubusercontent.com/asblPixels/ripdvd/main/scripts/install-linux.sh | bash
```

就这样！安装程序将：
1. 自动检测您的 Linux 发行版。
2. 安装所有必需的依赖。
3. 下载并安装 RipDvD。
4. 设置菜单项。

> **无需技术知识。** 复制、粘贴、按回车。

### 步骤 1 — 下载（手动）

```bash
git clone https://github.com/asblPixels/ripdvd.git
cd ripdvd
```

> 没有 `git`？从
> https://github.com/asblPixels/ripdvd/archive/refs/heads/main.zip 下载 ZIP 并解压。

### 步骤 2 — 安装依赖

```bash
sudo dnf install -y python3 python3-gobject gtk4 libadwaita zenity HandBrake HandBrake-cli
```

对于加密的商业 DVD，还请安装 `libdvdcss`：

```bash
sudo dnf install -y rpmfusion-free-release-tainted
sudo dnf install -y libdvdcss
```

### 步骤 3 — 运行安装程序

```bash
bash scripts/install.sh
```

安装程序将：
1. 验证 Python/GTK 依赖。
2. 安装 HandBrake (原生，如果原生不可用则使用 Flatpak 作为备用)。
3. 将应用程序复制到 `~/.local/bin/ripdvd-gui.py`。
4. 注册 GNOME 菜单项 (`ripdvd`)。

### 步骤 4 — 启动

```bash
python3 ~/.local/bin/ripdvd-gui.py
```

或在 GNOME 应用程序菜单中搜索 **RipDvD**。

### 验证一切正常

```bash
python3 -c "import gi; gi.require_version('Gtk','4.0'); gi.require_version('Adw','1'); print('GTK4/Adw OK')"
command -v HandBrakeCLI && echo "HandBrakeCLI OK"
```

两者都应打印 `OK`。

## 🎬 使用

1. 将 DVD 插入光驱。
2. 从 GNOME 应用程序菜单启动 **RipDvD** (或 `python3 ~/.local/bin/ripdvd-gui.py`)。
3. 应用程序自动扫描光盘并检测主电影 (最长标题)。
4. 从下拉菜单中选择 **音频语言** 和可选的 **字幕**。
5. 点击 **Rip DVD**。
6. 在日志窗口中观看实时进度。
7. 完成的 MKV 保存在 `~/Vidéos/Rips/` (或 `~/Videos/Rips/`)。

### 按钮

| 按钮 | 操作 |
|---|---|
| **Rip DVD** | 开始编码所选标题。 |
| **Arrêter** | 取消当前编码。 |
| **Reprendre** | 使用相同参数恢复/重试上次编码。 |
| **Quitter** | 关闭应用程序 (先停止任何正在运行的编码)。 |
| **Rescanner** | 重新分析光盘 (更换 DVD 后有用)。 |
| **Effacer log** | 清除实时输出窗口。 |

### CLI 版本

还提供了用于自动化的无头 bash 脚本：

```bash
bash src/ripdvd-cli.sh
```

它自动检测最长标题，并使用相同的默认参数进行提取，通过 `zenity` 显示进度。

## 🗂️ 项目结构

```
ripdvd/
├── src/
│   ├── ripdvd.py          # GTK4/libadwaita 图形界面应用程序
│   └── ripdvd-cli.sh      # 无头 CLI 提取器
├── scripts/
│   └── install.sh         # Fedora 安装程序
├── data/
│   └── ripdvd.desktop     # GNOME 菜单项
├── docs/
│   └── screenshot-main.png
├── .github/
│   ├── workflows/         # CI (语法检查)
│   └── ISSUE_TEMPLATE/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── .gitignore
```


### Windows

对于 Windows 10/11，从 https://github.com/asblPixels/ripdvd/archive/refs/heads/windows.zip 下载 ZIP，解压后双击 `install-windows.bat`。无需技术知识。

## 🐛 故障排除

### 应用程序无法启动 — `ModuleNotFoundError: No module named 'gi'`
安装 PyGObject：`sudo dnf install python3-gobject gtk4 libadwaita`

### 启动时 Segfault / 崩溃
确保使用最新版本 (线程安全的界面更新)。重新运行 `bash scripts/install.sh`。

### 未检测到 DVD (`/dev/sr0` 未找到)
- 检查光驱是否已连接：`lsblk | grep sr`
- 某些 USB 光驱需要插入后等待片刻；点击 **Rescanner**。

### 加密 DVD 黑屏 / "cannot read disc"
安装 `libdvdcss`：
```bash
sudo dnf install rpmfusion-free-release-tainted
sudo dnf install libdvdcss
```

### 输出文件为空
打开调试日志 (`~/.ripdvd-debug.log`) 或点击 **Voir le log de debug**。最后几行显示 HandBrake 错误。常见原因：
- 加密光盘缺少 `libdvdcss`。
- 没有 `--device=all` 的 HandBrake Flatpak (当前版本已修复)。
- `~/Vidéos/Rips/` 中磁盘空间不足。

### 旧 CPU 上编码缓慢
这是正常的 — 在 Sandy Bridge i3 上进行 x264 软件编码每部电影需要 ~10-15 分钟。应用程序使用 `medium` 预设以获得良好的质量/速度平衡。如需更快的提取，请在 `src/ripdvd.py` 中将 `--encoder-preset` 改为 `fast` 或 `veryfast`。

## 🙏 致谢

本项目离不开以下杰出工作：

- **[HandBrake](https://handbrake.fr/)** 及其团队 — 为一切提供动力的编码引擎。
- **[libdvdcss](https://www.videolan.org/developers/libdvdcss.html)** (VideoLAN) — DVD 解密。
- **[GNOME / GTK4 / libadwaita](https://gnome.org/)** — 界面工具包。
- **[RPM Fusion](https://rpmfusion.org/)** — Fedora 的打包。
- **[Fedora 项目](https://fedoraproject.org/)** — 操作系统。
- 所有开源贡献者和社区。

## 📚 来源与参考

- HandBrake CLI 文档：https://handbrake.fr/docs/en/latest/cli/
- libdvdcss 文档：https://www.videolan.org/developers/libdvdcss.html
- GTK4 / libadwaita 文档：https://docs.gtk.org/gtk4/ 和 https://gnome.pages.gitlab.gnome.org/libadwaita/
- PyGObject 文档：https://pygobject.readthedocs.io/
- RPM Fusion 配置：https://rpmfusion.org/Configuration
- Fedora 多媒体指南：https://docs.fedoraproject.org/en-US/quick-docs/assembly_installing-plugins-for-playing-movies-and-music/

## 👨‍💻 创建者

**RipDvD** 由 **[asblPixels](https://github.com/asblPixels)** 创建和维护，
作为其开源软件计划的一部分。

欢迎贡献、错误报告和功能请求！

## 📜 许可证

本项目采用 **MIT 许可证** — 详情请参阅 [LICENSE](LICENSE)。

## ⚠️ 法律声明

此工具旨在备份您拥有的 DVD 供个人使用。
解密受复制保护的光盘在您的国家可能受到限制。请查看当地法律。

---

<div align="center">

由 [asblPixels](https://github.com/asblPixels) 用 ❤️ 制作 · 开源 · MIT 许可证

</div>
