from __future__ import annotations

from dataclasses import dataclass

from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad


def text_to_array(content: str) -> bytes:
    ba: list[int] = []
    i = 0
    while i < len(content):
        c = ord(content[i])
        if c < 128:
            ba.append(c)
            i += 1
        elif c < 2048:
            ba.append((c >> 6) | 192)
            ba.append((c & 63) | 128)
            i += 1
        elif c < 65536:
            ba.append((c >> 12) | 224)
            ba.append(((c >> 6) & 63) | 128)
            ba.append((c & 63) | 128)
            i += 1
        else:
            ba.append((c >> 18) | 240)
            ba.append(((c >> 12) & 63) | 128)
            ba.append(((c >> 6) & 63) | 128)
            ba.append((c & 63) | 128)
            i += 2
    return bytes(ba)


KEY_SALT = text_to_array("hexo-blog-encrypt的作者们都是大帅比!")
IV_SALT = text_to_array("hexo-blog-encrypt是地表最强Hexo加密插件!")
KNOWN_PREFIX = b"<hbe-prefix></hbe-prefix>"


@dataclass(slots=True)
class DecryptResult:
    status: str
    content: str | None
    error: str | None = None


def derive_key_iv(password: str) -> tuple[bytes, bytes]:
    key = PBKDF2(password, KEY_SALT, dkLen=32, count=1024, hmac_hash_module=SHA256)
    iv = PBKDF2(password, IV_SALT, dkLen=16, count=512, hmac_hash_module=SHA256)
    return key, iv


def decrypt_and_verify(cipher_hex: str, hmac_digest: str | None, password: str) -> DecryptResult:
    try:
        key, iv = derive_key_iv(password)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(bytes.fromhex(cipher_hex))
        plaintext = unpad(plaintext, 16)
    except Exception as exc:  # noqa: BLE001
        return DecryptResult(status="wrong_password", content=None, error=f"解密失败: {exc}")

    if not plaintext.startswith(KNOWN_PREFIX):
        return DecryptResult(status="wrong_password", content=None, error="前缀不匹配")

    if hmac_digest:
        h = HMAC.new(key, digestmod=SHA256)
        h.update(plaintext)
        try:
            h.hexverify(hmac_digest)
        except ValueError:
            return DecryptResult(status="hmac_mismatch", content=None, error="HMAC 校验失败")

    content = plaintext[len(KNOWN_PREFIX) :].decode("utf-8", errors="replace")
    return DecryptResult(status="success", content=content)

