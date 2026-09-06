"""Opt-in use of the operating system's certificate store for outbound TLS.

Corporate proxies re-sign TLS with a private root that Python's bundled CA list does not know;
Hugging Face and dataset downloads then fail with `CERTIFICATE_VERIFY_FAILED`. Setting
`LEDGERLENS_NATIVE_TLS=1` makes every process (API, worker, CLI) trust the OS store instead.
No effect otherwise; never disables verification. Injection is idempotent — `truststore`'s own
`inject_into_ssl` is not, and a second call recurses inside `ssl.SSLContext`.
"""

from __future__ import annotations

import os

_injected = False


def maybe_inject_native_tls() -> bool:
    global _injected
    if os.environ.get("LEDGERLENS_NATIVE_TLS", "0") != "1":
        return False
    if _injected:
        return True
    import truststore

    truststore.inject_into_ssl()
    _injected = True
    return True
