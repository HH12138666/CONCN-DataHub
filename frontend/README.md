# 网页前端

Vue 与 Element Plus 页面，已恢复原网页的顶部导航、登录卡片和地图信息分栏。默认中文，支持英文切换。地图保留原天地图入口，在 SDK 不可用时启用 Leaflet/OpenStreetMap 备用底图。见 [恢复记录](../docs/需求规格说明书-甲方确认版-v1.0.md)。

当前没有配置可用的天地图密钥，默认使用备用底图。可在本目录 `.env` 中配置 `VITE_TIANDITU_KEY` 并重启前端；SDK 加载失败或超时会回退，不再阻塞整页加载。

在本目录执行：

```powershell
npm ci
npm run dev
```

开发地址为 `http://127.0.0.1:5173`，接口请求转发到 `http://127.0.0.1:8000`。需同时启动 [网站后端](../backend/README.md)。如需修改开发接口地址，可使用 `VITE_API_TARGET` 环境变量。

```powershell
npm run build
```

构建产物为本目录下的 `dist/`，后端已按新目录读取它。`npm run preview` 只预览静态构建产物，未配置 API 代理；需要完整登录、申请和下载功能时，请使用开发服务或由后端提供构建页面。

## 代码分工

- `src/api`：请求和下载操作。
- `src/stores`：用户、平台配置、初始化与消息提示。
- `src/locales`：语言选择、错误和状态文案；页面自身的成对文案暂保留在页面内。
- `src/views`：已有用户和管理员页面。
- `src/components`：共享地图。
- `src/router`：页面导航与访问提示；实际权限由后端决定。
- `src/styles`、`src/utils`：样式和格式化工具。

本次使用 Prettier 3.6.2 整理排版，没有增加运行依赖。后续需要同样格式时，可执行：

```powershell
npm exec --yes --package=prettier@3.6.2 -- prettier --write "src/**/*.{js,vue,css}" vite.config.js index.html
```
