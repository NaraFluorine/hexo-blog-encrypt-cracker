# hexo-blog-decrypt

English | 中文

## 这是什么

`hexo-blog-decrypt` 是一个面向 `hexo-blog-encrypt` 的本地离线测试工具：
- 输入 URL 抓取页面
- 提取提示文案 `message`、密文 `cipher_hex`、`hmac_digest`
- 使用词典+方块规则进行本地暴力枚举解密

## 项目结构

- `backend/`: Python 后端（抓取、解密、API、方块生成）
- `backend/dictionaries/`: 字典库目录（每行一个密码、每个 `.txt` 文件一个字典）
- `app-electron/`: Electron 桌面前端
- `cpp_accel/`: C++ 加速预留（pybind11）
- `PACKAGING.md`: 三端打包说明

## 当前方块规则（v0）

- 仅支持两种方块：`dict`（从字典库文件读取）、`charset`（固定长度字符枚举）
- 方块从左到右按字符串拼接生成候选密码，可在前端拖拽调整顺序
- 抓取结果默认不展示完整密文，仅用于提交到后端计算

## 快速开始

### 1) 后端环境

```bash
pip install -r backend/requirements.txt
```

### 2) 只做抓取测试

```bash
python -m backend.cli fetch --url "https://narafluorine.github.io/2024/09/02/20006_ToMakeTsingyunProblems/" --json
```

### 3) 启动 API 服务

```bash
python backend/server.py
```

### 4) 启动桌面前端

```bash
cd app-electron
npm install
npm run start
```

## 免责声明

1. 本项目用于个人技术研究、测试与教学。  
2. 仅支持本地离线枚举，不包含网络攻击能力。  
3. 请遵守法律法规与目标站点规则。  