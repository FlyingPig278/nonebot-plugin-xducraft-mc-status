# XDUCraft MC Status

基于 NoneBot 2 与 OneBot v11 的 Minecraft 服务器状态查询与像素风格状态图渲染插件。

支持查询 Minecraft 服务器在线状态、延迟、MOTD、版本与在线玩家信息，支持最多十三层的服务器树结构、原版样式 MOTD 与颜色代码（§）解析、方块材质背景排版，以及直连 Java 原生协议、高校公共接口与自建后端查询。

单独安装本插件与 Core 即可使用，管理面板为可选组件。若不使用 Web 管理面板，也可以通过 Python 代码完成配置激活。

运行整套机器人请看 [FlyingPig278/XDUCraft-bot](https://github.com/FlyingPig278/XDUCraft-bot)。

## 安装与加载

本软件包未发布至公共 PyPI 仓库，请使用 Git 地址安装。

### 1. 安装核心包与插件

在现有的 NoneBot 2.4.x 环境中，先安装 Core 核心包，再安装本插件。推荐同时安装管理面板插件以便在浏览器中配置服务器列表（管理面板运行不需要 Node.js）：

```bash
pip install "nonebot-plugin-xducraft-core[onebot] @ git+https://github.com/FlyingPig278/nonebot-plugin-xducraft-core.git@v0.3.0"
pip install "nonebot-plugin-xducraft-mc-status @ git+https://github.com/FlyingPig278/nonebot-plugin-xducraft-mc-status.git@v0.1.0"

# 可选：安装管理面板插件
pip install "nonebot-plugin-xducraft-admin @ git+https://github.com/FlyingPig278/nonebot-plugin-xducraft-admin.git@v0.1.0"
```

### 2. 配置插件加载

在 NoneBot 项目的 pyproject.toml 中向现有 plugins 列表追加以下模块（请保留已有的其他插件和适配器）：

```toml
[tool.nonebot]
plugins = [
    "xducraft_config",
    "xducraft_mc_status",
    # 如果安装了管理面板，添加以下加载项：
    # "xducraft_admin",
]
```

## 启用与首次使用

插件安装后，全局开关与各群开关默认处于关闭状态。

### 1. 开启插件

方式一：使用 Web 管理面板（推荐）

如果加载了 [nonebot-plugin-xducraft-admin](https://github.com/FlyingPig278/nonebot-plugin-xducraft-admin)，请参考其说明配置面板密码（操作系统环境变量 `WEB_ADMIN_PASSWORD`）并启动机器人，访问管理面板（默认地址 http://127.0.0.1:8765）：
1. 在“插件”页面开启“MC 服务器状态”全局开关。
2. 在“群聊”页面选择对应群，开启本群的“MC 服务器状态”插件开关。
3. 点击该群的配置卡片，在服务器列表中添加服务器地址（例如 play.example.com）并保存。

方式二：不使用 Web 管理面板

如果不运行管理面板，请参考 Core 文档中的[不使用网页时启用插件](https://github.com/FlyingPig278/nonebot-plugin-xducraft-core#不使用网页时启用插件)。通过一次性脚本调用 Core 配置接口，同时开启全局开关与目标群的插件开关。由于 Core 在前置检查中会拦截未在群中启用的插件消息，且未安装 Features 插件时不存在 `/功能` 命令，因此必须在 Core 中同时配置全局与群开关，配置完成后即可在群内使用。

### 2. 发起查询

在已启用的群内发送以下指令即可发起查询：

- `/mcs play.example.com`：临时查询指定服务器地址。
- `/mcs`：查询本群已配置的服务器状态总览图。
- `/mcs all`：显示本群全部服务器节点，包含离线与隐藏节点。
- `/mcs texture=dirt` 或 `/mcs texture=random`：临时更换背景材质出图。
- `/mcs auth`：查看或配置群内登录认证模式说明。
- `/mcs source`：查看或切换本群查询源类型（例如 `/mcs source set protocol` 或 `/mcs source set custom`）及后端 API 地址。

## 配置项说明

### 群级配置

群级配置保存在 Core 数据库中，可在 Web 管理面板的群设置中修改，或在群内使用指令查看：

- `servers`：本群服务器树。支持最多 13 层的父子层级关系。每个节点包含服务器 IP、端口、备注说明、显示别名、标签文字与颜色、认证模式（正版、离线、统一登录等）、排序权重，以及是否在状态图中隐藏真实地址。
- `status_api_source` 与 `status_api_url`：状态查询源类型与后端接口地址。查询源支持在网页管理面板中下拉选择，或通过指令设置（如 `protocol` 直连 Java 协议、`custom` 自建独立后端、`auto` 自动等）。自建后端适用于目标服务器处于独立网络、机器人无法直接访问 Minecraft 端口但能访问 HTTP 代理的场景，属于可选组件，正常情况下无需搭建后端。
- `show_offline_by_default`：状态总览图中是否默认显示离线服务器，默认为关闭。
- `footer`：状态图底部显示的说明文案。

### 全局渲染参数

全局渲染参数用于自定义图片生成样式。可以在环境配置文件中配置，也可以在 Core 数据库的全局覆盖项中修改，修改后重启机器人生效：

- `MCS_BRAND`：状态图顶部左侧品牌文字，支持 § 颜色代码。
- `MCS_TITLE`：状态图主标题文字，支持 § 颜色代码。
- `MCS_CREDIT`：状态图底部版权文字，支持 § 颜色代码。
- `MCS_SHOW_GENERATED_AT`：是否在底部显示生成时间，布尔值，默认为 true。
- `MCS_TEXTURE`：默认背景材质文件名。留空时根据群号自动选择固定材质，亦可设置为 random、none 或具体方块 PNG 文件名（如 dirt.png、stone.png，必须以 .png 结尾）。临时出图命令 `/mcs texture=dirt` 可直接使用方块名。
- `MCS_WIDTH`：画布逻辑宽度，范围 480 到 1600，默认 640。
- `MCS_SCALE`：渲染缩放倍数，可选 2 或 4，默认 2。
- `MCS_MIN_HEIGHT`：画布最小高度，默认 480；设为 0 表示根据内容自适应高度。

## 离线预览与开发工具

仓库 scripts 目录提供了本地离线渲染脚本，用于在不启动机器人、不连接网络的情况下预览排版和方块材质：

- 离线工具运行驱动为 ~none，不需要安装 FastAPI，也不需要启动机器人实例。
- 预览工具与管理面板均不需要安装 Node.js。

```bash
# 离线渲染状态图排版预览（使用预设测试数据）
python scripts/preview_mc_status.py
python scripts/preview_mc_status.py --list

# 预览指定方块材质的平铺效果
python scripts/preview_mc_texture.py dirt
python scripts/preview_mc_texture.py cyan_glazed_terracotta --size 512
```

## 本地开发与测试

克隆本仓库后，可以在本地虚拟环境中安装开发依赖并运行测试：

```bash
pip install "nonebot-plugin-xducraft-core[onebot] @ git+https://github.com/FlyingPig278/nonebot-plugin-xducraft-core.git@v0.3.0"
pip install -e ".[dev]"
pytest
python -m build
```

## 数据存储与历史迁移

历史配置文件 server_data.json 仅用于首次启动时单次导入。Core 首次启动会自动将其导入 Core SQLite 数据库的 mc_status 命名空间中，导入完成后旧文件不再保存新设置，后续修改以数据库为准。查询过程中获取的服务器图标等临时缓存由缓存目录统一管理，不写入持久化配置。

如需指定外部持久化数据存储目录，请在启动 Python 进程前配置操作系统环境变量 XDUCRAFT_DATA_DIR 为绝对路径。

## 许可证与资产说明

本项目源码采用 MIT 许可证开源，详见 [LICENSE](LICENSE)。

项目中包含的第三方字体与美术资源遵循其原授权协议，不属于本项目的 MIT 授权范围：
- 内置思源黑体历史版本字体 resources/fonts/SourceHanSansCN-Medium.otf 版权归 Adobe Systems Incorporated 所有，遵循 Apache License 2.0，许可文本参见 [LICENSES/SourceHanSansCN-Apache-2.0.txt](LICENSES/SourceHanSansCN-Apache-2.0.txt)，详细说明见 [NOTICE](NOTICE)。
- Monocraft.otf 与 minecraft-five-bold.otf 遵循 SIL Open Font License 1.1。
- VONWAONBITMAP-12PX.TTF 遵循 CC0 1.0 协议。
- 原版 Minecraft 方块材质、界面图标及相关字体属于 Mojang AB / Microsoft 资产，其使用受 Mojang 最终用户许可协议约束。相关历史遗留资产在未取得单独重新授权前作为遗留资产保留，详见仓库 [NOTICE](NOTICE) 说明。
