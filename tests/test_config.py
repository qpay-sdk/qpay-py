"""Tests for QPayConfig."""

from __future__ import annotations

import os

import pytest

from qpay import QPayConfig


class TestQPayConfig:
    """Tests for QPayConfig dataclass and from_env()."""

    def test_from_env_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """from_env() loads all required environment variables."""
        monkeypatch.setenv("QPAY_BASE_URL", "https://merchant.qpay.mn")
        monkeypatch.setenv("QPAY_USERNAME", "user")
        monkeypatch.setenv("QPAY_PASSWORD", "pass")
        monkeypatch.setenv("QPAY_INVOICE_CODE", "INV001")
        monkeypatch.setenv("QPAY_CALLBACK_URL", "https://example.com/cb")

        cfg = QPayConfig.from_env()

        assert cfg.base_url == "https://merchant.qpay.mn"
        assert cfg.username == "user"
        assert cfg.password == "pass"
        assert cfg.invoice_code == "INV001"
        assert cfg.callback_url == "https://example.com/cb"

    def test_from_env_missing_all(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """from_env() raises ValueError when all vars are missing."""
        for key in [
            "QPAY_BASE_URL",
            "QPAY_USERNAME",
            "QPAY_PASSWORD",
            "QPAY_INVOICE_CODE",
            "QPAY_CALLBACK_URL",
        ]:
            monkeypatch.delenv(key, raising=False)

        with pytest.raises(ValueError, match="QPAY_BASE_URL"):
            QPayConfig.from_env()

    def test_from_env_missing_one(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """from_env() raises ValueError naming the missing variable."""
        monkeypatch.setenv("QPAY_BASE_URL", "https://merchant.qpay.mn")
        monkeypatch.setenv("QPAY_USERNAME", "user")
        monkeypatch.setenv("QPAY_PASSWORD", "pass")
        monkeypatch.setenv("QPAY_INVOICE_CODE", "INV001")
        monkeypatch.delenv("QPAY_CALLBACK_URL", raising=False)

        with pytest.raises(ValueError, match="QPAY_CALLBACK_URL"):
            QPayConfig.from_env()

    def test_from_env_empty_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """from_env() treats empty string as missing."""
        monkeypatch.setenv("QPAY_BASE_URL", "https://merchant.qpay.mn")
        monkeypatch.setenv("QPAY_USERNAME", "")
        monkeypatch.setenv("QPAY_PASSWORD", "pass")
        monkeypatch.setenv("QPAY_INVOICE_CODE", "INV001")
        monkeypatch.setenv("QPAY_CALLBACK_URL", "https://example.com/cb")

        with pytest.raises(ValueError, match="QPAY_USERNAME"):
            QPayConfig.from_env()

    def test_from_env_missing_multiple(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """from_env() lists all missing variables in the error message."""
        monkeypatch.setenv("QPAY_BASE_URL", "https://merchant.qpay.mn")
        monkeypatch.delenv("QPAY_USERNAME", raising=False)
        monkeypatch.delenv("QPAY_PASSWORD", raising=False)
        monkeypatch.setenv("QPAY_INVOICE_CODE", "INV001")
        monkeypatch.setenv("QPAY_CALLBACK_URL", "https://example.com/cb")

        with pytest.raises(ValueError) as exc_info:
            QPayConfig.from_env()

        msg = str(exc_info.value)
        assert "QPAY_USERNAME" in msg
        assert "QPAY_PASSWORD" in msg

    def test_direct_construction(self) -> None:
        """QPayConfig can be constructed directly."""
        cfg = QPayConfig(
            base_url="https://test.qpay.mn",
            username="u",
            password="p",
            invoice_code="IC",
            callback_url="https://cb.example.com",
        )
        assert cfg.base_url == "https://test.qpay.mn"
        assert cfg.username == "u"
