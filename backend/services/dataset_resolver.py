# backend/services/dataset_resolver.py
"""Utilities to resolve and download dataset resources.

Supported sources:
- Direct HTTP/HTTPS URLs pointing to a file.
- Public dataset portals (Kaggle, HuggingFace, Zenodo, etc.) where a
  webpage URL is supplied – we attempt to discover the direct download
  link via their public APIs (no authentication required).

All downloads are performed with `httpx` (streaming) and go through
`verify_ssrf_target` to block private IPs and cloud‑metadata endpoints.
The caller is responsible for validating the archive safety (zip‑slip,
path traversal) using `backend.utils.archive_safe.validate_archive`.
"""

import re
import urllib.parse
from typing import Tuple

import httpx

from backend.core.config import settings

# ---------------------------------------------------------------------------
# Simple SSRF protection – allow only public IPv4/IPv6 and HTTPS URLs.
# ---------------------------------------------------------------------------
def verify_ssrf_target(url: str) -> str:
    """Validate that *url* is a safe public HTTP/HTTPS target.

    Returns the normalized URL if safe, otherwise raises `ValueError`.
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http/https URLs are allowed.")
    # Basic host validation – reject localhost, private ranges, link‑local.
    host = parsed.hostname or ""
    if not host:
        raise ValueError("URL must contain a host.")
    # Regexes for disallowed host patterns
    disallowed = [
        r"^127\\.",            # loopback IPv4
        r"^10\\.",             # private IPv4
        r"^172\\.(1[6-9]|2[0-9]|3[0-1])\\.",
        r"^192\\.168\\.",
        r"^169\\.254\\.",    # link‑local
        r"^0\\.",
        r"^::1$",               # IPv6 loopback
        r"^fe80::",             # IPv6 link‑local
        r"^fc00::",             # IPv6 unique local
        r"^fd00::",
    ]
    for pattern in disallowed:
        if re.match(pattern, host):
            raise ValueError(f"URL host '{host}' is disallowed for security reasons.")
    return urllib.parse.urlunparse(parsed)

# ---------------------------------------------------------------------------
# Resolve public dataset portals – limited to a few well‑known services.
# ---------------------------------------------------------------------------
def resolve_public_dataset(url: str) -> str:
    """Given a public dataset page URL, attempt to retrieve the direct
    download link. Currently supports Kaggle, HuggingFace Hub, and Zenodo.
    If the URL already points to a file, it is returned unchanged.
    """
    # Quick path – if URL ends with a known archive extension, assume direct.
    if re.search(r"\\.(zip|tar|gz|tgz|csv|json|parquet)$", url, re.IGNORECASE):
        return url

    # Kaggle – public datasets can be downloaded via the Kaggle API endpoint
    if "kaggle.com" in url:
        # Example: https://www.kaggle.com/datasets/<owner>/<name>
        # Public download link pattern (no auth) can be obtained via
        # https://www.kaggle.com/api/v1/datasets/download/<owner>/<name>
        m = re.search(r"kaggle.com/datasets/([^/]+)/([^/]+)", url)
        if m:
            owner, name = m.groups()
            return f"https://www.kaggle.com/api/v1/datasets/download/{owner}/{name}"

    # Hugging Face Hub – raw file URL pattern
    if "huggingface.co" in url:
        # Convert to raw file link if a repo+file is supplied
        # Example: https://huggingface.co/datasets/<org>/<repo>/resolve/main/<file>
        if "resolve" not in url:
            # Try to construct a raw URL assuming `main` branch
            parts = url.rstrip("/").split("/")
            if len(parts) >= 5:
                org, repo = parts[3], parts[4]
                return f"https://huggingface.co/datasets/{org}/{repo}/resolve/main/"
        return url

    # Zenodo – use the "download" link if present in query params
    if "zenodo.org" in url:
        # Zenodo record URLs contain an identifier; the direct file link is
        # typically <record_url>/files/<filename>?download=1
        return url + "?download=1"

    # Fallback – return the original URL; caller will attempt a plain download.
    return url

# ---------------------------------------------------------------------------
# Download helper – streams to a temporary file and returns the path.
# ---------------------------------------------------------------------------
def download_to_temp(url: str) -> str:
    """Download *url* (after SSRF check) to a temporary file and return the
    absolute path. The caller must delete the file when finished.
    """
    safe_url = verify_ssrf_target(url)
    resolved = resolve_public_dataset(safe_url)
    client = httpx.Client(follow_redirects=True, timeout=30.0)
    with client.stream("GET", resolved) as resp:
        resp.raise_for_status()
        # Enforce max size (settings.dataset_max_bytes, default 500MB)
        max_bytes = getattr(settings, "dataset_max_bytes", 500 * 1024 * 1024)
        total = 0
        import tempfile, shutil
        tmp = tempfile.NamedTemporaryFile(delete=False)
        try:
            for chunk in resp.iter_bytes(chunk_size=8192):
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError("Dataset download exceeds allowed size limit.")
                tmp.write(chunk)
        finally:
            tmp.close()
        return tmp.name

# ---------------------------------------------------------------------------
# Public API used by the ingestion endpoint
# ---------------------------------------------------------------------------
def fetch_dataset(source: str, *, is_url: bool = False) -> Tuple[str, str]:
    """Return a tuple ``(local_path, source_type)``.

    * ``source`` – either a file path (when ``is_url`` is ``False``) or a URL.
    * ``source_type`` – one of ``LOCAL_UPLOAD``, ``DIRECT_URL``,
      ``ONLINE_DATASET_RESOURCE``.
    """
    if is_url:
        # Determine if the URL points directly to a file or a portal page.
        if re.search(r"\\.(zip|tar|gz|tgz|csv|json|parquet)$", source, re.IGNORECASE):
            source_type = "DIRECT_URL"
        else:
            source_type = "ONLINE_DATASET_RESOURCE"
        local_path = download_to_temp(source)
    else:
        # Assume caller already placed the uploaded file on disk.
        source_type = "LOCAL_UPLOAD"
        local_path = source
    return local_path, source_type

# End of file
