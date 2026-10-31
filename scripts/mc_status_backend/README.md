# MC Status Backend (FastAPI)

独立部署的 Minecraft Java 版状态查询后端，供机器人通过 HTTP 拉取服务器在线状态与 MOTD 信息。
主要用于目标服务器位于独立网络区域，机器人无法直接连接 Minecraft 端口，但可以访问该 HTTP 服务的场景。后端仅提供 HTTP 查询接口，不提供网络穿透功能，服务地址必须能被机器人直接访问。

## 接口说明

- `GET /health`：健康检查接口，返回 `{"ok": true, "timeout": 3.0}`（`ok` 为布尔值 `true`，`timeout` 为当前查询超时秒数，默认 `3.0`）
- `GET /status?query=<server_address>`：查询目标服务器状态

响应字段：
- `online`（布尔值）、`hostname`、`port`、`original_query`、`ip`
- 在线时返回：`ping`、`version`、`protocol`、`players`、`description`、`description_raw`、`favicon`
- 查询失败时返回：`error`

## 依赖与安装

后端支持脱离机器人独立运行。

### 1. 基础依赖安装

在独立的 Python 虚拟环境中安装基础运行依赖：

```bash
pip install "fastapi>=0.93,<1" "uvicorn~=0.38.0" "mcstatus~=12.0.6"
```

### 2. 可选 Core 协议增强

后端代码在导入时会检测环境中是否存在 Core 核心包：
- 未安装 Core 时：自动回退至原生 mcstatus 库实现，支持直接将 app.py 复制到目标机器单文件部署。
- 安装了 Core 时：若环境中安装了 nonebot-plugin-xducraft-core，将复用 Core 的原生协议实现，获取更完整的原始 MOTD 与玩家样本信息。

## 环境变量与服务启动

FastAPI 与 Uvicorn 默认不会自动读取当前目录的 .env 文件。请通过操作系统环境变量配置，或显式指定环境变量文件。
启动前需要切换到脚本所在目录：

```bash
cd scripts/mc_status_backend
```

支持的环境变量：
- `MC_STATUS_BACKEND_TIMEOUT`：单次状态查询超时时间（秒，浮点数，默认 3.0）。

### 启动方式一：直接设置操作系统环境变量（推荐）

在终端中设置环境变量并启动服务：

Linux 或 macOS：
```bash
export MC_STATUS_BACKEND_TIMEOUT=5.0
uvicorn app:app --host 0.0.0.0 --port 8099
```

Windows PowerShell：
```powershell
$env:MC_STATUS_BACKEND_TIMEOUT="5.0"
uvicorn app:app --host 0.0.0.0 --port 8099
```

### 启动方式二：通过指定环境变量文件启动

若希望通过 .env 文件管理变量，请安装 python-dotenv 并使用 `--env-file` 参数启动：

```bash
pip install python-dotenv
uvicorn app:app --env-file .env --host 0.0.0.0 --port 8099
```

## 机器人对接配置

在部署后端并确保机器人能正常访问后端端口后，可在对应群内配置接入：

1. 设置查询源为自建后端：
   `/mcs source set custom`
2. 设置本群查询 API 地址：
   `/mcs api set http://<后端IP或域名>:8099/status`
3. 也可以在 Web 管理面板的群卡片中直接配置查询源与 API 接口。
