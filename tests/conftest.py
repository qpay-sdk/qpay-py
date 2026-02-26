"""Common fixtures for QPay SDK tests."""

from __future__ import annotations

import time
from typing import Any

import httpx
import pytest
import respx

from qpay import QPayConfig, QPayClient, AsyncQPayClient

BASE_URL = "https://merchant.qpay.mn"


def make_token_response(
    *,
    access_token: str = "test-access-token",
    refresh_token: str = "test-refresh-token",
    expires_in: int | None = None,
    refresh_expires_in: int | None = None,
) -> dict[str, Any]:
    """Build a token response dict with sensible defaults."""
    now = int(time.time())
    return {
        "token_type": "Bearer",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": expires_in if expires_in is not None else now + 3600,
        "refresh_expires_in": (
            refresh_expires_in if refresh_expires_in is not None else now + 86400
        ),
        "scope": "default_scope",
        "not-before-policy": "0",
        "session_state": "test-session",
    }


def make_invoice_response(invoice_id: str = "inv-123") -> dict[str, Any]:
    """Build a sample invoice response dict."""
    return {
        "invoice_id": invoice_id,
        "qr_text": "qr-text-data",
        "qr_image": "base64-qr-image",
        "qPay_shortUrl": "https://qpay.mn/q/inv-123",
        "urls": [
            {
                "name": "Khan Bank",
                "description": "Khan Bank app",
                "logo": "https://qpay.mn/logo/khan.png",
                "link": "khanbank://pay?q=inv-123",
            }
        ],
    }


def make_payment_detail(payment_id: str = "pay-456") -> dict[str, Any]:
    """Build a sample payment detail dict."""
    return {
        "payment_id": payment_id,
        "payment_status": "PAID",
        "payment_fee": "0",
        "payment_amount": "10000",
        "payment_currency": "MNT",
        "payment_date": "2024-01-15T10:00:00",
        "payment_wallet": "khan",
        "transaction_type": "P2P",
        "object_type": "INVOICE",
        "object_id": "inv-123",
        "card_transactions": [],
        "p2p_transactions": [
            {
                "transaction_bank_code": "050",
                "account_bank_code": "050",
                "account_bank_name": "Khan Bank",
                "account_number": "5000123456",
                "status": "SUCCESS",
                "amount": "10000",
                "currency": "MNT",
                "settlement_status": "SETTLED",
            }
        ],
    }


def make_payment_check_response() -> dict[str, Any]:
    """Build a sample payment check response dict."""
    return {
        "count": 1,
        "paid_amount": 10000.0,
        "rows": [
            {
                "payment_id": "pay-456",
                "payment_status": "PAID",
                "payment_amount": "10000",
                "trx_fee": "0",
                "payment_currency": "MNT",
                "payment_wallet": "khan",
                "payment_type": "P2P",
                "card_transactions": [],
                "p2p_transactions": [],
            }
        ],
    }


def make_payment_list_response() -> dict[str, Any]:
    """Build a sample payment list response dict."""
    return {
        "count": 1,
        "rows": [
            {
                "payment_id": "pay-456",
                "payment_date": "2024-01-15T10:00:00",
                "payment_status": "PAID",
                "payment_fee": "0",
                "payment_amount": "10000",
                "payment_currency": "MNT",
                "payment_wallet": "khan",
                "payment_name": "Test Payment",
                "payment_description": "Order #123",
                "qr_code": "qr-data",
                "paid_by": "customer@test.com",
                "object_type": "INVOICE",
                "object_id": "inv-123",
            }
        ],
    }


def make_ebarimt_response() -> dict[str, Any]:
    """Build a sample ebarimt response dict."""
    return {
        "id": "eb-789",
        "ebarimt_by": "MERCHANT",
        "g_wallet_id": "w-001",
        "g_wallet_customer_id": "wc-001",
        "ebarimt_receiver_type": "83",
        "ebarimt_receiver": "",
        "ebarimt_district_code": "23",
        "ebarimt_bill_type": "1",
        "g_merchant_id": "m-001",
        "merchant_branch_code": "branch-01",
        "merchant_register_no": "1234567",
        "g_payment_id": "pay-456",
        "paid_by": "customer@test.com",
        "object_type": "INVOICE",
        "object_id": "inv-123",
        "amount": "10000",
        "vat_amount": "1000",
        "city_tax_amount": "100",
        "ebarimt_qr_data": "ebarimt-qr",
        "ebarimt_lottery": "AB12345678",
        "barimt_status": "CREATED",
        "barimt_status_date": "2024-01-15T10:00:00",
        "ebarimt_receiver_phone": "99001122",
        "tax_type": "1",
        "merchant_tin": "1234567",
        "ebarimt_receipt_id": "receipt-001",
        "created_by": "system",
        "created_date": "2024-01-15T10:00:00",
        "updated_by": "system",
        "updated_date": "2024-01-15T10:00:00",
        "status": True,
        "barimt_items": [],
        "barimt_transactions": [],
        "barimt_histories": [],
    }


@pytest.fixture
def config() -> QPayConfig:
    """Return a test QPayConfig."""
    return QPayConfig(
        base_url=BASE_URL,
        username="test_user",
        password="test_pass",
        invoice_code="TEST_INVOICE",
        callback_url="https://example.com/callback",
    )


@pytest.fixture
def mock_router() -> respx.MockRouter:
    """Return a started respx mock router (non-context-manager version)."""
    router = respx.MockRouter(base_url=BASE_URL, assert_all_called=False)
    router.start()
    yield router  # type: ignore[misc]
    router.stop()


@pytest.fixture
def sync_client(config: QPayConfig, mock_router: respx.MockRouter) -> QPayClient:
    """Return a sync QPayClient wired to the mock transport."""
    transport = httpx.MockTransport(mock_router.handler)
    http_client = httpx.Client(transport=transport, timeout=5.0)
    client = QPayClient(config, http_client=http_client)
    yield client  # type: ignore[misc]
    client.close()


@pytest.fixture
def async_client(
    config: QPayConfig, mock_router: respx.MockRouter
) -> AsyncQPayClient:
    """Return an async QPayClient wired to the mock transport."""
    transport = httpx.MockTransport(mock_router.handler)
    http_client = httpx.AsyncClient(transport=transport, timeout=5.0)
    client = AsyncQPayClient(config, http_client=http_client)
    return client
