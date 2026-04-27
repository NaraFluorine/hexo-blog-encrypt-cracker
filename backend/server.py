from __future__ import annotations

from pathlib import Path
import sys

import uvicorn

# 保证无论当前工作目录在哪，都能导入 backend 包。
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.api import app


def main() -> None:
    uvicorn.run(app, host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()

