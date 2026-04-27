from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable


@dataclass(slots=True)
class PasswordBlock:
    type: str
    config: dict


def _dict_candidates(config: dict) -> list[str]:
    values = config.get("values", [])
    return [str(v) for v in values]


def _charset_candidates(config: dict) -> Iterable[str]:
    charset = config.get("charset", "")
    length = int(config.get("length", 1))
    if not charset:
        return []
    result: list[str] = []
    for letters in product(charset, repeat=length):
        result.append("".join(letters))
    return result


def block_candidates(block: PasswordBlock) -> Iterable[str]:
    if block.type == "dict":
        return _dict_candidates(block.config)
    if block.type == "charset":
        return _charset_candidates(block.config)
    return []


def iter_password_candidates(blocks: list[PasswordBlock], limit: int = 100000) -> Iterable[str]:
    pools = [list(block_candidates(block)) for block in blocks]
    if not pools:
        return
    count = 0
    for items in product(*pools):
        yield "".join(items)
        count += 1
        if count >= limit:
            return

