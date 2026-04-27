from __future__ import annotations

from pathlib import Path
from threading import Lock, Thread
import time

from fastapi import FastAPI
from pydantic import BaseModel, Field

try:
    from .crypto.accelerated_check import quick_check_prefix
    from .crypto.hbe_decrypt import decrypt_and_verify
    from .generator.blocks import PasswordBlock, iter_password_candidates
    from .scraper.fetch_hexo import fetch_hexo_encrypted_page
except ImportError:
    from backend.crypto.accelerated_check import quick_check_prefix
    from backend.crypto.hbe_decrypt import decrypt_and_verify
    from backend.generator.blocks import PasswordBlock, iter_password_candidates
    from backend.scraper.fetch_hexo import fetch_hexo_encrypted_page

app = FastAPI(title="hexo-blog-decrypt backend", version="0.1.0")
DICTIONARIES_DIR = Path(__file__).resolve().parent / "dictionaries"

job_state: dict = {
    "running": False,
    "tested": 0,
    "found_password": None,
    "elapsed_seconds": 0.0,
    "status": "idle",
}
job_lock = Lock()


class FetchRequest(BaseModel):
    url: str


class BlockModel(BaseModel):
    type: str = Field(pattern="^(dict|charset)$")
    config: dict


class CrackStartRequest(BaseModel):
    cipher_hex: str
    hmac_digest: str | None = None
    blocks: list[BlockModel]
    limit: int = 100000


def _read_dictionary_file(dict_name: str) -> list[str]:
    if not dict_name:
        raise ValueError("字典名不能为空")
    safe_name = Path(dict_name).name
    if safe_name != dict_name:
        raise ValueError("字典名非法")
    dict_file = DICTIONARIES_DIR / safe_name
    if not dict_file.exists() or not dict_file.is_file():
        raise ValueError("字典不存在")
    values: list[str] = []
    with dict_file.open("r", encoding="utf-8") as fp:
        for line in fp:
            word = line.strip()
            if word:
                values.append(word)
    return values


def _hydrate_blocks(blocks: list[BlockModel]) -> list[PasswordBlock]:
    output: list[PasswordBlock] = []
    for block in blocks:
        if block.type == "dict":
            dict_name = str(block.config.get("dict_name", "")).strip()
            values = _read_dictionary_file(dict_name)
            output.append(PasswordBlock(type="dict", config={"values": values}))
            continue

        charset = str(block.config.get("charset", ""))
        length = int(block.config.get("length", 1))
        if length <= 0:
            raise ValueError("charset 方块 length 必须 >= 1")
        output.append(PasswordBlock(type="charset", config={"charset": charset, "length": length}))
    return output


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/fetch")
def api_fetch(payload: FetchRequest) -> dict:
    result = fetch_hexo_encrypted_page(payload.url)
    return result.to_dict()


@app.get("/api/dictionaries")
def list_dictionaries() -> dict:
    DICTIONARIES_DIR.mkdir(parents=True, exist_ok=True)
    files = []
    for path in sorted(DICTIONARIES_DIR.glob("*.txt")):
        with path.open("r", encoding="utf-8") as fp:
            total = sum(1 for line in fp if line.strip())
        files.append({"name": path.name, "count": total})
    return {"ok": True, "dictionaries": files}


def _crack_worker(payload: CrackStartRequest) -> None:
    start = time.time()
    tested = 0
    try:
        block_objs = _hydrate_blocks(payload.blocks)
        with job_lock:
            job_state["running"] = True
            job_state["status"] = "running"
            job_state["tested"] = 0
            job_state["found_password"] = None
            job_state["elapsed_seconds"] = 0.0

        for password in iter_password_candidates(block_objs, limit=payload.limit):
            tested += 1
            if not quick_check_prefix(payload.cipher_hex, password):
                continue
            result = decrypt_and_verify(payload.cipher_hex, payload.hmac_digest, password)
            with job_lock:
                job_state["tested"] = tested
            if result.status == "success":
                elapsed = round(time.time() - start, 3)
                with job_lock:
                    job_state["running"] = False
                    job_state["status"] = "success"
                    job_state["found_password"] = password
                    job_state["elapsed_seconds"] = elapsed
                return

        elapsed = round(time.time() - start, 3)
        with job_lock:
            job_state["running"] = False
            job_state["status"] = "exhausted"
            job_state["elapsed_seconds"] = elapsed
    except Exception as exc:  # noqa: BLE001
        elapsed = round(time.time() - start, 3)
        with job_lock:
            job_state["running"] = False
            job_state["status"] = f"error: {exc}"
            job_state["elapsed_seconds"] = elapsed


@app.post("/api/crack/start")
def crack_start(payload: CrackStartRequest) -> dict:
    with job_lock:
        if job_state["running"]:
            return {"ok": False, "error": "已有任务在运行"}
    thread = Thread(target=_crack_worker, args=(payload,), daemon=True)
    thread.start()
    return {"ok": True, "status": "started"}


@app.get("/api/crack/status")
def crack_status() -> dict:
    with job_lock:
        return {"ok": True, "state": dict(job_state)}

