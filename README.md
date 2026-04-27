# hexo-blog-decrypt

English | 中文

Local offline cracking playground for `hexo-blog-encrypt`:
- fetch encrypted blog page by URL
- extract `message`, `cipher_hex`, `hmac_digest`
- brute-force locally with dictionary + block rules

## Quick start

```bash
pip install -r backend/requirements.txt
python -m backend.cli fetch --url "https://narafluorine.github.io/2024/09/02/20006_ToMakeTsingyunProblems/" --json
python backend/server.py
```

Desktop frontend:

```bash
cd app-electron
npm install
npm run start
```

Packaging guidance: see `PACKAGING.md`.