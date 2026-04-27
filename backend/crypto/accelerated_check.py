from __future__ import annotations

try:
    import hbe_accel  # type: ignore
except Exception:  # noqa: BLE001
    hbe_accel = None


def quick_check_prefix(cipher_hex: str, password: str) -> bool:
    if hbe_accel is None:
        # fallback: C++ 模块未就绪时始终继续完整解密流程
        return True
    return bool(hbe_accel.quick_check_prefix(cipher_hex, password))

