# 已有操作命令索引

命令实现在 `backend/datahub/cli.py`，从 `backend` 目录使用对应 Python 环境执行。这里不复制命令实现。

| 命令 | 作用 |
| --- | --- |
| `python -m datahub.cli --help` | 查看帮助，不修改数据库 |
| `python -m datahub.cli bootstrap` | 全新本地环境初始化，交互输入 MySQL 管理密码 |
| `python -m datahub.cli admin` | 交互创建管理员 |
| `python -m datahub.cli import-catalog 文件路径` | 追加导入经过校验的 JSON 流域目录 |
| `python -m datahub.cli publish-local` | 校验本地源文件与七级目录，发布本地验证版本；仅限 development 和本地 MySQL，相同版本拒绝覆盖 |

**本机已经完成初始化，不要重跑 `bootstrap`。** 它会拒绝覆盖已有配置、数据库或应用用户。

单独的目录导入不会发布版本。`publish-local` 会同时接入经过校验的真实目录与本地版本；当前机器已经完成，不必重复执行。

仓库根目录运行 `./scripts/start-local.ps1` 可启动前端、后端和裁切服务。
`build_pfmask_windows.py` 用固定版本的官方源码重建本机域生成器。

Windows 本地环境可将表中的 `python` 替换为 `..\.venv\Scripts\python.exe`。前端和网站启动说明分别见 [前端](../frontend/README.md) 与 [后端](../backend/README.md)。
