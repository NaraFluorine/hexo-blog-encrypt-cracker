from __future__ import annotations

import argparse
import json

try:
    from .scraper.fetch_hexo import fetch_hexo_encrypted_page
except ImportError:
    from backend.scraper.fetch_hexo import fetch_hexo_encrypted_page


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hexo-blog-decrypt")
    sub = parser.add_subparsers(dest="command", required=True)

    fetch_cmd = sub.add_parser("fetch", help="抓取并提取 hexo-blog-encrypt 页面数据")
    fetch_cmd.add_argument("--url", required=True, help="目标文章 URL")
    fetch_cmd.add_argument("--json", action="store_true", help="输出 JSON")
    return parser


def run_fetch(url: str, as_json: bool) -> int:
    result = fetch_hexo_encrypted_page(url)
    payload = result.to_dict()

    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"URL: {payload['url']}")
    print(f"状态: {'成功' if payload['ok'] else '失败'}")
    print(f"message: {payload.get('message') or '<空>'}")
    print(f"hmac_digest: {payload.get('hmac_digest') or '<空>'}")
    cipher_hex = payload.get("cipher_hex") or ""
    preview = f"{cipher_hex[:80]}..." if len(cipher_hex) > 80 else cipher_hex
    print(f"cipher_hex 预览: {preview or '<空>'}")
    if payload["errors"]:
        print("错误:")
        for err in payload["errors"]:
            print(f"  - {err}")
    return 0 if payload["ok"] else 2


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "fetch":
        return run_fetch(args.url, args.json)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

