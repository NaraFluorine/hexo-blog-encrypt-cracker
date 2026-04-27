from __future__ import annotations

from bs4 import BeautifulSoup
import requests

try:
    from ..models import FetchResult
except ImportError:
    from backend.models import FetchResult

SCRIPT_SELECTOR = "script#hbeData[type='hbeData']"
MESSAGE_SELECTORS = [
    ".hbe-input-label-content",
    "span.hbe-input-label-content-default",
    "span.hbe-input-label-content",
]


def fetch_hexo_encrypted_page(url: str, timeout: float = 12.0) -> FetchResult:
    result = FetchResult(url=url, message=None, cipher_hex=None, hmac_digest=None)
    result.selectors["cipher"] = SCRIPT_SELECTOR
    result.selectors["message"] = ",".join(MESSAGE_SELECTORS)

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        result.errors.append(f"请求失败: {exc}")
        return result

    html = response.content.decode("utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")

    script_tag = soup.select_one(SCRIPT_SELECTOR)
    if script_tag is None:
        result.errors.append("未找到密文脚本节点 script#hbeData[type='hbeData']")
    else:
        raw_cipher = script_tag.get_text(strip=True)
        if raw_cipher:
            result.cipher_hex = raw_cipher
        else:
            result.errors.append("密文脚本节点为空")
        hmac_digest = (script_tag.get("data-hmacdigest") or "").strip()
        if hmac_digest:
            result.hmac_digest = hmac_digest
        else:
            result.errors.append("未找到 data-hmacdigest")

    for selector in MESSAGE_SELECTORS:
        message_node = soup.select_one(selector)
        if message_node:
            message = message_node.get_text(" ", strip=True)
            if message:
                result.message = message
                result.selectors["message_hit"] = selector
                break

    if not result.message:
        result.errors.append("未找到提示 message")

    return result

