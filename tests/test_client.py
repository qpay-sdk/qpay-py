"""Tests for QPayClient (synchronous)."""

from __future__ import annotations

import json
import time

import httpx
import pytest
import respx

from qpay import (
    QPayClient,
    QPayConfig,
    QPayError,
)
from qpay.types import (
    CreateEbarimtInvoiceRequest,
    CreateEbarimtRequest,
    CreateInvoiceRequest,
    CreateSimpleInvoiceRequest,
    EbarimtInvoiceLine,
    Offset,
    PaymentCancelRequest,
    PaymentCheckRequest,
    PaymentListRequest,
    PaymentRefundRequest,
)

from .conftest import (
    BASE_URL,
    make_ebarimt_response,
    make_invoice_response,
    make_payment_check_response,
    make_payment_detail,
    make_payment_list_response,
    make_token_response,
)


class TestGetToken:
    """Tests for QPayClient.get_token()."""

    def test_success(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        token_data = make_token_response()
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=token_data)
        )

        token = sync_client.get_token()

        assert token.access_token == "test-access-token"
        assert token.refresh_token == "test-refresh-token"
        assert token.token_type == "Bearer"

    def test_auth_failure(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(
                401,
                json={"error": "AUTHENTICATION_FAILED", "message": "Bad credentials"},
            )
        )

        with pytest.raises(QPayError) as exc_info:
            sync_client.get_token()

        assert exc_info.value.status_code == 401
        assert exc_info.value.code == "AUTHENTICATION_FAILED"


class TestRefreshToken:
    """Tests for QPayClient.refresh_token()."""

    def test_success(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        # First get a token so there is a refresh_token stored
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        sync_client.get_token()

        new_token_data = make_token_response(
            access_token="new-access", refresh_token="new-refresh"
        )
        mock_router.post("/v2/auth/refresh").mock(
            return_value=httpx.Response(200, json=new_token_data)
        )

        token = sync_client.refresh_token()

        assert token.access_token == "new-access"
        assert token.refresh_token == "new-refresh"


class TestAutoTokenManagement:
    """Tests for automatic token acquisition on API calls."""

    def test_auto_gets_token_on_first_request(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        """Client auto-authenticates when making a request without a token."""
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.post("/v2/invoice").mock(
            return_value=httpx.Response(200, json=make_invoice_response())
        )

        req = CreateSimpleInvoiceRequest(
            invoice_code="TEST",
            sender_invoice_no="INV-001",
            invoice_receiver_code="terminal",
            invoice_description="Test invoice",
            amount=1000.0,
            callback_url="https://example.com/cb",
        )
        result = sync_client.create_simple_invoice(req)

        assert result.invoice_id == "inv-123"

    def test_auto_refresh_when_token_expired(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        """Client uses refresh token when access token is expired."""
        now = int(time.time())
        # Access token already expired, but refresh token still valid
        expired_token = make_token_response(
            expires_in=now - 100,
            refresh_expires_in=now + 86400,
        )
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=expired_token)
        )
        sync_client.get_token()

        refreshed_token = make_token_response(access_token="refreshed-access")
        mock_router.post("/v2/auth/refresh").mock(
            return_value=httpx.Response(200, json=refreshed_token)
        )
        mock_router.get("/v2/payment/pay-1").mock(
            return_value=httpx.Response(200, json=make_payment_detail("pay-1"))
        )

        result = sync_client.get_payment("pay-1")
        assert result.payment_id == "pay-1"


class TestCreateInvoice:
    """Tests for invoice creation methods."""

    def test_create_invoice(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.post("/v2/invoice").mock(
            return_value=httpx.Response(200, json=make_invoice_response("inv-full"))
        )

        req = CreateInvoiceRequest(
            invoice_code="TEST",
            sender_invoice_no="INV-002",
            invoice_receiver_code="terminal",
            invoice_description="Full invoice",
            amount=5000.0,
            callback_url="https://example.com/cb",
        )
        result = sync_client.create_invoice(req)

        assert result.invoice_id == "inv-full"
        assert result.qr_text == "qr-text-data"
        assert len(result.urls) == 1
        assert result.urls[0].name == "Khan Bank"

    def test_create_simple_invoice(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.post("/v2/invoice").mock(
            return_value=httpx.Response(200, json=make_invoice_response())
        )

        req = CreateSimpleInvoiceRequest(
            invoice_code="TEST",
            sender_invoice_no="INV-003",
            invoice_receiver_code="terminal",
            invoice_description="Simple invoice",
            amount=1000.0,
            callback_url="https://example.com/cb",
        )
        result = sync_client.create_simple_invoice(req)

        assert result.invoice_id == "inv-123"
        assert result.qpay_short_url == "https://qpay.mn/q/inv-123"

    def test_create_ebarimt_invoice(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.post("/v2/invoice").mock(
            return_value=httpx.Response(200, json=make_invoice_response())
        )

        req = CreateEbarimtInvoiceRequest(
            invoice_code="TEST",
            sender_invoice_no="INV-004",
            invoice_receiver_code="terminal",
            invoice_description="Ebarimt invoice",
            tax_type="1",
            district_code="23",
            callback_url="https://example.com/cb",
            lines=[
                EbarimtInvoiceLine(
                    tax_product_code="1234567",
                    line_description="Product A",
                    line_quantity="1",
                    line_unit_price="10000",
                )
            ],
        )
        result = sync_client.create_ebarimt_invoice(req)

        assert result.invoice_id == "inv-123"

    def test_create_invoice_error(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.post("/v2/invoice").mock(
            return_value=httpx.Response(
                400,
                json={
                    "error": "INVOICE_CODE_INVALID",
                    "message": "Invalid invoice code",
                },
            )
        )

        req = CreateSimpleInvoiceRequest(
            invoice_code="INVALID",
            sender_invoice_no="INV-ERR",
            invoice_receiver_code="terminal",
            invoice_description="Bad invoice",
            amount=1000.0,
            callback_url="https://example.com/cb",
        )

        with pytest.raises(QPayError) as exc_info:
            sync_client.create_simple_invoice(req)

        assert exc_info.value.code == "INVOICE_CODE_INVALID"
        assert exc_info.value.status_code == 400


class TestCancelInvoice:
    """Tests for QPayClient.cancel_invoice()."""

    def test_success(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.delete("/v2/invoice/inv-123").mock(
            return_value=httpx.Response(200)
        )

        # Should not raise
        sync_client.cancel_invoice("inv-123")

    def test_not_found(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.delete("/v2/invoice/bad-id").mock(
            return_value=httpx.Response(
                404,
                json={"error": "INVOICE_NOTFOUND", "message": "Invoice not found"},
            )
        )

        with pytest.raises(QPayError) as exc_info:
            sync_client.cancel_invoice("bad-id")

        assert exc_info.value.status_code == 404


class TestGetPayment:
    """Tests for QPayClient.get_payment()."""

    def test_success(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.get("/v2/payment/pay-456").mock(
            return_value=httpx.Response(200, json=make_payment_detail())
        )

        result = sync_client.get_payment("pay-456")

        assert result.payment_id == "pay-456"
        assert result.payment_status == "PAID"
        assert result.payment_amount == "10000"
        assert len(result.p2p_transactions) == 1
        assert result.p2p_transactions[0].account_bank_name == "Khan Bank"

    def test_not_found(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.get("/v2/payment/bad-id").mock(
            return_value=httpx.Response(
                404,
                json={"error": "PAYMENT_NOTFOUND", "message": "Payment not found"},
            )
        )

        with pytest.raises(QPayError) as exc_info:
            sync_client.get_payment("bad-id")

        assert exc_info.value.code == "PAYMENT_NOTFOUND"


class TestCheckPayment:
    """Tests for QPayClient.check_payment()."""

    def test_success(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.post("/v2/payment/check").mock(
            return_value=httpx.Response(200, json=make_payment_check_response())
        )

        req = PaymentCheckRequest(object_type="INVOICE", object_id="inv-123")
        result = sync_client.check_payment(req)

        assert result.count == 1
        assert result.paid_amount == 10000.0
        assert len(result.rows) == 1
        assert result.rows[0].payment_id == "pay-456"


class TestListPayments:
    """Tests for QPayClient.list_payments()."""

    def test_success(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.post("/v2/payment/list").mock(
            return_value=httpx.Response(200, json=make_payment_list_response())
        )

        req = PaymentListRequest(
            object_type="INVOICE",
            object_id="inv-123",
            start_date="2024-01-01",
            end_date="2024-12-31",
            offset=Offset(page_number=1, page_limit=10),
        )
        result = sync_client.list_payments(req)

        assert result.count == 1
        assert len(result.rows) == 1
        assert result.rows[0].payment_id == "pay-456"
        assert result.rows[0].payment_wallet == "khan"


class TestCancelPayment:
    """Tests for QPayClient.cancel_payment()."""

    def test_success(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.delete("/v2/payment/cancel/pay-456").mock(
            return_value=httpx.Response(200)
        )

        req = PaymentCancelRequest(
            callback_url="https://example.com/cb", note="test cancel"
        )
        # Should not raise
        sync_client.cancel_payment("pay-456", req)

    def test_already_canceled(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.delete("/v2/payment/cancel/pay-456").mock(
            return_value=httpx.Response(
                400,
                json={
                    "error": "PAYMENT_ALREADY_CANCELED",
                    "message": "Already canceled",
                },
            )
        )

        req = PaymentCancelRequest()

        with pytest.raises(QPayError) as exc_info:
            sync_client.cancel_payment("pay-456", req)

        assert exc_info.value.code == "PAYMENT_ALREADY_CANCELED"


class TestRefundPayment:
    """Tests for QPayClient.refund_payment()."""

    def test_success(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.delete("/v2/payment/refund/pay-456").mock(
            return_value=httpx.Response(200)
        )

        req = PaymentRefundRequest(
            callback_url="https://example.com/cb", note="test refund"
        )
        # Should not raise
        sync_client.refund_payment("pay-456", req)


class TestCreateEbarimt:
    """Tests for QPayClient.create_ebarimt()."""

    def test_success(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.post("/v2/ebarimt_v3/create").mock(
            return_value=httpx.Response(200, json=make_ebarimt_response())
        )

        req = CreateEbarimtRequest(
            payment_id="pay-456",
            ebarimt_receiver_type="83",
        )
        result = sync_client.create_ebarimt(req)

        assert result.id == "eb-789"
        assert result.ebarimt_lottery == "AB12345678"
        assert result.amount == "10000"
        assert result.status is True


class TestCancelEbarimt:
    """Tests for QPayClient.cancel_ebarimt()."""

    def test_success(
        self,
        sync_client: QPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.delete("/v2/ebarimt_v3/pay-456").mock(
            return_value=httpx.Response(200, json=make_ebarimt_response())
        )

        result = sync_client.cancel_ebarimt("pay-456")

        assert result.id == "eb-789"


class TestContextManager:
    """Tests for QPayClient context manager support."""

    def test_context_manager(
        self,
        config: QPayConfig,
        mock_router: respx.MockRouter,
    ) -> None:
        transport = httpx.MockTransport(mock_router.handler)
        http = httpx.Client(transport=transport)
        with QPayClient(config, http_client=http) as client:
            mock_router.post("/v2/auth/token").mock(
                return_value=httpx.Response(200, json=make_token_response())
            )
            token = client.get_token()
            assert token.access_token == "test-access-token"
