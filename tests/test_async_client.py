"""Tests for AsyncQPayClient."""

from __future__ import annotations

import time

import httpx
import pytest
import respx

from qpay import (
    AsyncQPayClient,
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

pytestmark = pytest.mark.asyncio


class TestAsyncGetToken:
    """Tests for AsyncQPayClient.get_token()."""

    async def test_success(
        self,
        async_client: AsyncQPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        token_data = make_token_response()
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=token_data)
        )

        token = await async_client.get_token()

        assert token.access_token == "test-access-token"
        assert token.refresh_token == "test-refresh-token"
        assert token.token_type == "Bearer"

    async def test_auth_failure(
        self,
        async_client: AsyncQPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(
                401,
                json={"error": "AUTHENTICATION_FAILED", "message": "Bad credentials"},
            )
        )

        with pytest.raises(QPayError) as exc_info:
            await async_client.get_token()

        assert exc_info.value.status_code == 401
        assert exc_info.value.code == "AUTHENTICATION_FAILED"


class TestAsyncRefreshToken:
    """Tests for AsyncQPayClient.refresh_token()."""

    async def test_success(
        self,
        async_client: AsyncQPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        await async_client.get_token()

        new_token_data = make_token_response(
            access_token="new-access", refresh_token="new-refresh"
        )
        mock_router.post("/v2/auth/refresh").mock(
            return_value=httpx.Response(200, json=new_token_data)
        )

        token = await async_client.refresh_token()

        assert token.access_token == "new-access"
        assert token.refresh_token == "new-refresh"


class TestAsyncAutoTokenManagement:
    """Tests for automatic token acquisition on async API calls."""

    async def test_auto_gets_token_on_first_request(
        self,
        async_client: AsyncQPayClient,
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
            sender_invoice_no="INV-001",
            invoice_receiver_code="terminal",
            invoice_description="Test invoice",
            amount=1000.0,
            callback_url="https://example.com/cb",
        )
        result = await async_client.create_simple_invoice(req)

        assert result.invoice_id == "inv-123"

    async def test_auto_refresh_when_token_expired(
        self,
        async_client: AsyncQPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        now = int(time.time())
        expired_token = make_token_response(
            expires_in=now - 100,
            refresh_expires_in=now + 86400,
        )
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=expired_token)
        )
        await async_client.get_token()

        refreshed_token = make_token_response(access_token="refreshed-access")
        mock_router.post("/v2/auth/refresh").mock(
            return_value=httpx.Response(200, json=refreshed_token)
        )
        mock_router.get("/v2/payment/pay-1").mock(
            return_value=httpx.Response(200, json=make_payment_detail("pay-1"))
        )

        result = await async_client.get_payment("pay-1")
        assert result.payment_id == "pay-1"


class TestAsyncCreateInvoice:
    """Tests for async invoice creation methods."""

    async def test_create_invoice(
        self,
        async_client: AsyncQPayClient,
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
        result = await async_client.create_invoice(req)

        assert result.invoice_id == "inv-full"
        assert result.qr_text == "qr-text-data"
        assert len(result.urls) == 1

    async def test_create_simple_invoice(
        self,
        async_client: AsyncQPayClient,
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
        result = await async_client.create_simple_invoice(req)

        assert result.invoice_id == "inv-123"

    async def test_create_ebarimt_invoice(
        self,
        async_client: AsyncQPayClient,
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
        result = await async_client.create_ebarimt_invoice(req)

        assert result.invoice_id == "inv-123"

    async def test_create_invoice_error(
        self,
        async_client: AsyncQPayClient,
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
            await async_client.create_simple_invoice(req)

        assert exc_info.value.code == "INVOICE_CODE_INVALID"


class TestAsyncCancelInvoice:
    """Tests for AsyncQPayClient.cancel_invoice()."""

    async def test_success(
        self,
        async_client: AsyncQPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.delete("/v2/invoice/inv-123").mock(
            return_value=httpx.Response(200)
        )

        await async_client.cancel_invoice("inv-123")

    async def test_not_found(
        self,
        async_client: AsyncQPayClient,
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
            await async_client.cancel_invoice("bad-id")

        assert exc_info.value.status_code == 404


class TestAsyncGetPayment:
    """Tests for AsyncQPayClient.get_payment()."""

    async def test_success(
        self,
        async_client: AsyncQPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.get("/v2/payment/pay-456").mock(
            return_value=httpx.Response(200, json=make_payment_detail())
        )

        result = await async_client.get_payment("pay-456")

        assert result.payment_id == "pay-456"
        assert result.payment_status == "PAID"
        assert len(result.p2p_transactions) == 1

    async def test_not_found(
        self,
        async_client: AsyncQPayClient,
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
            await async_client.get_payment("bad-id")

        assert exc_info.value.code == "PAYMENT_NOTFOUND"


class TestAsyncCheckPayment:
    """Tests for AsyncQPayClient.check_payment()."""

    async def test_success(
        self,
        async_client: AsyncQPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.post("/v2/payment/check").mock(
            return_value=httpx.Response(200, json=make_payment_check_response())
        )

        req = PaymentCheckRequest(object_type="INVOICE", object_id="inv-123")
        result = await async_client.check_payment(req)

        assert result.count == 1
        assert result.paid_amount == 10000.0
        assert result.rows[0].payment_id == "pay-456"


class TestAsyncListPayments:
    """Tests for AsyncQPayClient.list_payments()."""

    async def test_success(
        self,
        async_client: AsyncQPayClient,
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
        result = await async_client.list_payments(req)

        assert result.count == 1
        assert result.rows[0].payment_wallet == "khan"


class TestAsyncCancelPayment:
    """Tests for AsyncQPayClient.cancel_payment()."""

    async def test_success(
        self,
        async_client: AsyncQPayClient,
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
        await async_client.cancel_payment("pay-456", req)

    async def test_already_canceled(
        self,
        async_client: AsyncQPayClient,
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
            await async_client.cancel_payment("pay-456", req)

        assert exc_info.value.code == "PAYMENT_ALREADY_CANCELED"


class TestAsyncRefundPayment:
    """Tests for AsyncQPayClient.refund_payment()."""

    async def test_success(
        self,
        async_client: AsyncQPayClient,
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
        await async_client.refund_payment("pay-456", req)


class TestAsyncCreateEbarimt:
    """Tests for AsyncQPayClient.create_ebarimt()."""

    async def test_success(
        self,
        async_client: AsyncQPayClient,
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
        result = await async_client.create_ebarimt(req)

        assert result.id == "eb-789"
        assert result.ebarimt_lottery == "AB12345678"


class TestAsyncCancelEbarimt:
    """Tests for AsyncQPayClient.cancel_ebarimt()."""

    async def test_success(
        self,
        async_client: AsyncQPayClient,
        mock_router: respx.MockRouter,
    ) -> None:
        mock_router.post("/v2/auth/token").mock(
            return_value=httpx.Response(200, json=make_token_response())
        )
        mock_router.delete("/v2/ebarimt_v3/pay-456").mock(
            return_value=httpx.Response(200, json=make_ebarimt_response())
        )

        result = await async_client.cancel_ebarimt("pay-456")

        assert result.id == "eb-789"


class TestAsyncContextManager:
    """Tests for AsyncQPayClient async context manager support."""

    async def test_async_context_manager(
        self,
        config: QPayConfig,
        mock_router: respx.MockRouter,
    ) -> None:
        transport = httpx.MockTransport(mock_router.handler)
        http = httpx.AsyncClient(transport=transport)
        async with AsyncQPayClient(config, http_client=http) as client:
            mock_router.post("/v2/auth/token").mock(
                return_value=httpx.Response(200, json=make_token_response())
            )
            token = await client.get_token()
            assert token.access_token == "test-access-token"
