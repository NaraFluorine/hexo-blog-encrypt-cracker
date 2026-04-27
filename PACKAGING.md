# 三端打包说明（Win/macOS/Linux）

## 1. 打包目标
- 前端：Electron 应用（`app-electron`）
- 后端：Python FastAPI 服务（`backend`）
- 产物：`exe` / `dmg` / `AppImage`

## 2. 后端打包
建议先用 PyInstaller 生成单文件可执行：

```bash
pip install pyinstaller -r backend/requirements.txt
pyinstaller --onefile --name hexo-backend backend/server.py
```

将产物拷贝到 `app-electron/resources/backend/`，供 Electron 主进程启动。

## 3. 前端打包
在 `app-electron` 目录执行：

```bash
npm install
npm run pack:win
npm run pack:mac
npm run pack:linux
```

## 4. 启动约定
- 主进程拉起本地后端进程（默认 `127.0.0.1:8765`）
- 前端通过 preload bridge 访问后端 API

## 5. 发布建议
- 在 CI 里矩阵构建三平台产物
- 发布时附带默认词典和示例方块配置

