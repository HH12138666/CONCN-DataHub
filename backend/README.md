# 网站后端

从仓库根目录安装网站依赖：

```powershell
.venv\Scripts\python.exe -m pip install -r backend/requirements/web.txt
```

本机已有 `backend/.env` 和新 MySQL 数据库，直接复用；不要再次执行初始化。换到全新环境时，配置示例见 `.env.example`，全新初始化命令见 [操作命令索引](../scripts/README.md)。

在仓库根目录打开终端后启动网站：

```powershell
cd backend
..\.venv\Scripts\python.exe app.py
```

默认监听 `http://127.0.0.1:8000`。前端开发页面由 Vite 提供；前端构建后，后端也可直接提供 `frontend/dist` 页面。数据库连接、SMTP、源数据和任务目录通过环境变量配置；`.env` 只在本地保存。

后台裁切需要另一个终端及可用的科学处理环境。在 Linux 科学处理环境安装 `requirements/worker.txt`，配置源数据与 `pfmask-to-pfsol` 后，从 `backend` 目录运行：

```bash
python -m datahub.workers.queue
```

`--once` 会领取并处理一次任务，不是只读检查。不要用它做生产环境的健康探测。网站接口健康检查为 `GET /api/health`。

模块职责见 [代码框架与整理记录](../docs/维护与优化文档-v1.0.md)。

## 本机环境配置记录

本次已在仓库 `.venv` 中安装网站、GeoPandas、Rasterio、NumPy 和 pftools 依赖。
七级边界读取与重投影、七级模板栅格抽样读取、PFB 写入/读取往返检查均已通过；`pip check` 无依赖冲突。

Windows Python 3.14 安装 pftools 时，其依赖 PyYAML 6.0.1 的 C 扩展需要编译环境。
本机使用官方安装脚本支持的纯 Python 模式完成安装，从仓库根目录可复现：

```powershell
$env:PYYAML_FORCE_LIBYAML = '0'
.venv\Scripts\python.exe -m pip install -r backend/requirements/worker.txt
```

该选项见 [PyYAML 6.0.1 官方安装脚本](https://github.com/yaml/pyyaml/blob/6.0.1/setup.py)。
它仅控制本次安装，不改变应用数据或业务规则。

2026-09-09 已从官方源码构建本机 `pfmask-to-pfsol`，配置路径并启动 Worker。七级真实目录及本地验证版本已接入 MySQL，真实 ZIP 下载通过验收，详见 [下载包规范](../docs/下载包内容与文字维护.md)。
