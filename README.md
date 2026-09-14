# CONCN DataHub

基于 Vue、Flask、MySQL 的 ParFlow 流域数据共享平台，支持流域地图、注册登录、申请审核、异步裁切和授权下载。当前代码来自原 ParFlow-CONCN 共享平台并持续改造，保留科学工具来源信息。

## 功能

- 默认中文，可切换英文；省市定位、七级流域地图和14位编号精确搜索。
- 每账号免审核获取两个不同小流域编码，同编码可重复下载；大流域和额外小流域可申请审核。
- 下载用途填写、后台任务、个人下载/申请/通知、管理员账号搜索及内容管理。
- 当前数据版本 concn1.1，完整ZIP包含10个数据及元信息文件。

## 项目目录

| 目录 | 用途 |
|---|---|
| frontend | Vue网页、地图和管理页面 |
| backend | Flask API、MySQL业务、后台队列 |
| concnshare | ParFlow科学裁切工具 |
| database | 新数据库结构、迁移及默认规则 |
| tests | 后端、裁切及前端测试（前端测试位于frontend/tests） |
| scripts | 本地启动、工具构建、目录导入等脚本 |
| docs | 需求、功能说明、API、数据库和运维文档 |
| deploy | 部署注意事项 |
| Fig | 科学说明中引用的示意图 |

## 获取代码后需要准备

本仓库不包含源数据、数据库内容、账号密码、天地图密钥、Python虚拟环境、node_modules、运行缓存或下载ZIP。仅克隆源码不会恢复原机器的账号和数据。

1. 准备Python、Node.js和MySQL，具体依赖见 backend/requirements 和 frontend/package.json。
2. 创建Python虚拟环境，安装 backend/requirements/web.txt；运行裁切还需 worker.txt 中的科学依赖及 pfmask-to-pfsol。
3. 按 backend/.env.example 配置本地 backend/.env；前端按 frontend/.env.example 创建本地配置。不得提交真实.env。
4. 全新数据库按 database/README.md 和后端CLI初始化并导入目录。已有数据库不要重复bootstrap。
5. 科学源数据单独传输并配置路径。跨Windows/Linux需重新构建并验证科学工具，不能直接使用Windows可执行文件。
6. 在frontend运行 npm ci 和 npm run build。后端 app.py 提供生产构建页面与API，后台裁切另运行 python -m datahub.workers.queue。

当前开发电脑在根目录运行 ./scripts/start-local.ps1。默认新环境后端端口8000；本机已配置8100。前端5173代理地址通过 VITE_API_TARGET 配置，与后端端口保持一致。局域网入口使用实际服务器IP，127.0.0.1只用于本机。

## 文档

- [需求规格说明书](docs/需求规格说明书.md)
- [网站功能使用说明](docs/网站功能使用说明.md)
- [后端API接口文档](docs/后端API接口文档.md)
- [数据库逐字段说明](docs/数据库逐字段说明-v1.0.md)
- [下载包内容](docs/下载包内容与文字维护.md)
- [后端](backend/README.md)、[前端](frontend/README.md)、[测试](tests/README.md)
- [文档目录](docs/README.md)、[源码发布说明](docs/源码发布说明.md)

## 来源与部署边界

原始项目：https://github.com/ParFlowCommunity/ParFlow-CONCN-Share-Platform 。科学工具作者及来源声明保留；本次整理没有替上游或数据新增授权条款，具体使用许可请以原作者和数据提供者声明为准。

公网服务器、HTTPS、SMTP及正式数据许可仍需按实际环境配置验收。将代码上传GitHub不等于网站已经上线，也不包含数据发布。
