"""Ledgerlens core: domain model, migrations, repositories, settings, storage, jobs.

Native-TLS injection (opt-in via LEDGERLENS_NATIVE_TLS=1) must happen before any library
captures `ssl.SSLContext` (boto3/urllib3 do so at import), so it runs here, at package import.
"""

from ledgerlens_core.tls import maybe_inject_native_tls

maybe_inject_native_tls()
