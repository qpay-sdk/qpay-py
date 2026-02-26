"""Tests for QPayError and error utilities."""

from __future__ import annotations

import json

import pytest

from qpay import QPayError, is_qpay_error
from qpay.errors import (
    ERR_AUTHENTICATION_FAILED,
    ERR_INVOICE_NOT_FOUND,
    ERR_PAYMENT_NOT_FOUND,
)


class TestQPayError:
    """Tests for QPayError construction and from_response()."""

    def test_from_response_json_body(self) -> None:
        """from_response() parses JSON error body."""
        body = json.dumps({
            "error": "INVOICE_NOTFOUND",
            "message": "Invoice not found",
        }).encode()

        err = QPayError.from_response(404, body)

        assert err.status_code == 404
        assert err.code == "INVOICE_NOTFOUND"
        assert err.message == "Invoice not found"
        assert err.raw_body == body.decode()

    def test_from_response_non_json_body(self) -> None:
        """from_response() handles non-JSON body gracefully."""
        body = b"Internal Server Error"

        err = QPayError.from_response(500, body)

        assert err.status_code == 500
        assert err.code == "Internal Server Error"
        assert err.message == "Internal Server Error"

    def test_from_response_empty_body(self) -> None:
        """from_response() handles empty body."""
        err = QPayError.from_response(401, b"")

        assert err.status_code == 401
        assert err.code == "Unauthorized"
        assert err.message == ""

    def test_from_response_json_missing_fields(self) -> None:
        """from_response() handles JSON with missing error/message fields."""
        body = json.dumps({"other": "data"}).encode()

        err = QPayError.from_response(400, body)

        # code falls back to HTTP status phrase when error field is empty
        assert err.status_code == 400
        assert err.code == "Bad Request"

    def test_str_representation(self) -> None:
        """QPayError str() includes code, message, and status."""
        err = QPayError(
            status_code=403,
            code="PERMISSION_DENIED",
            message="Access denied",
            raw_body='{"error":"PERMISSION_DENIED","message":"Access denied"}',
        )

        s = str(err)
        assert "PERMISSION_DENIED" in s
        assert "Access denied" in s
        assert "403" in s

    def test_is_exception(self) -> None:
        """QPayError is an Exception subclass."""
        err = QPayError(status_code=500, code="ERR", message="fail")
        assert isinstance(err, Exception)

    def test_direct_construction_defaults(self) -> None:
        """QPayError has sensible defaults."""
        err = QPayError()
        assert err.status_code == 0
        assert err.code == ""
        assert err.message == ""
        assert err.raw_body == ""


class TestIsQPayError:
    """Tests for is_qpay_error() helper."""

    def test_with_qpay_error(self) -> None:
        """Returns the QPayError when given one."""
        err = QPayError(status_code=404, code="NOT_FOUND", message="not found")
        result = is_qpay_error(err)
        assert result is err

    def test_with_other_exception(self) -> None:
        """Returns None for non-QPayError exceptions."""
        err = ValueError("something else")
        result = is_qpay_error(err)
        assert result is None

    def test_with_none(self) -> None:
        """Returns None when given None."""
        result = is_qpay_error(None)
        assert result is None

    def test_with_base_exception(self) -> None:
        """Returns None for BaseException that is not QPayError."""
        err = KeyboardInterrupt()
        result = is_qpay_error(err)
        assert result is None


class TestErrorConstants:
    """Verify error code constants match expected strings."""

    def test_authentication_failed(self) -> None:
        assert ERR_AUTHENTICATION_FAILED == "AUTHENTICATION_FAILED"

    def test_invoice_not_found(self) -> None:
        assert ERR_INVOICE_NOT_FOUND == "INVOICE_NOTFOUND"

    def test_payment_not_found(self) -> None:
        assert ERR_PAYMENT_NOT_FOUND == "PAYMENT_NOTFOUND"
