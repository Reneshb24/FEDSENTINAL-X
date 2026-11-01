"""
Unit tests for SSRF Protection and Dataset Path Traversal Prevention.
"""

import pytest
from fastapi import HTTPException
from backend.services.dataset_service import _validate_safe_url


def test_ssrf_blocks_localhost_and_loopback():
    forbidden_urls = [
        "http://localhost:8000/api/v1/data",
        "http://127.0.0.1:8000/admin",
        "http://127.0.1.1/secret",
        "https://127.0.0.1:443/",
        "http://0.0.0.0:8000/",
    ]
    for url in forbidden_urls:
        with pytest.raises(HTTPException) as exc_info:
            _validate_safe_url(url)
        assert exc_info.value.status_code == 400
        assert "Forbidden" in exc_info.value.detail or "localhost" in exc_info.value.detail


def test_ssrf_blocks_private_subnets():
    # RFC 1918 addresses
    private_ips = [
        "http://10.0.0.1/data.npz",
        "http://172.16.0.5/dataset.npz",
        "http://192.168.1.100/records.npz",
        "http://169.254.169.254/latest/meta-data/",  # AWS metadata endpoint
    ]
    for url in private_ips:
        with pytest.raises(HTTPException) as exc_info:
            _validate_safe_url(url)
        assert exc_info.value.status_code == 400
        assert "restricted" in exc_info.value.detail or "private" in exc_info.value.detail


def test_ssrf_rejects_invalid_schemes():
    invalid_schemes = [
        "ftp://example.com/dataset.npz",
        "gopher://example.com/",
        "file:///etc/passwd",
    ]
    for url in invalid_schemes:
        with pytest.raises(HTTPException) as exc_info:
            _validate_safe_url(url)
        assert exc_info.value.status_code == 400
