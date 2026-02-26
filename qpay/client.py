"""QPay V2 API client with auto token management."""

from __future__ import annotations

import threading
import time
from typing import Any, Optional, TypeVar, Type

import httpx

from .config import QPayConfig
from .errors import QPayError
from .types import (
    CreateEbarimtInvoiceRequest,
    CreateEbarimtRequest,
    CreateInvoiceRequest,
    CreateSimpleInvoiceRequest,
    EbarimtResponse,
    InvoiceResponse,
    PaymentCancelRequest,
    PaymentCheckRequest,
    PaymentCheckResponse,
    PaymentDetail,
    PaymentListRequest,
    PaymentListResponse,
    PaymentRefundRequest,
    TokenResponse,
)

_TOKEN_BUFFER_SECONDS = 30

T = TypeVar("T")


class QPayClient:
    """Synchronous QPay V2 API client with automatic token management.

    The client automatically obtains and refreshes access tokens as needed.
    Token management is thread-safe.
    """

    def __init__(
        self,
        config: QPayConfig,
        *,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self._config = config
        self._http = http_client or httpx.Client(timeout=30.0)
        self._owns_http = http_client is None
        self._lock = threading.Lock()

        self._access_token = ""
        self._refresh_token = ""
        self._expires_at: int = 0
        self._refresh_expires_at: int = 0

    def close(self) -> None:
        """Close the underlying HTTP client if it was created by this instance."""
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> QPayClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # --- Auth ---

    def get_token(self) -> TokenResponse:
        """Authenticate with QPay using Basic Auth and return a new token pair."""
        token = self._get_token_request()
        with self._lock:
            self._store_token(token)
        return token

    def refresh_token(self) -> TokenResponse:
        """Use the current refresh token to obtain a new access token."""
        with self._lock:
            refresh_tok = self._refresh_token
        token = self._do_refresh_token_http(refresh_tok)
        with self._lock:
            self._store_token(token)
        return token

    # --- Invoice ---

    def create_invoice(self, request: CreateInvoiceRequest) -> InvoiceResponse:
        """Create a detailed invoice with full options. POST /v2/invoice"""
        data = self._do_request("POST", "/v2/invoice", body=request.to_dict())
        return InvoiceResponse.from_dict(data)

    def create_simple_invoice(
        self, request: CreateSimpleInvoiceRequest
    ) -> InvoiceResponse:
        """Create a simple invoice with minimal fields. POST /v2/invoice"""
        data = self._do_request("POST", "/v2/invoice", body=request.to_dict())
        return InvoiceResponse.from_dict(data)

    def create_ebarimt_invoice(
        self, request: CreateEbarimtInvoiceRequest
    ) -> InvoiceResponse:
        """Create an invoice with ebarimt (tax) information. POST /v2/invoice"""
        data = self._do_request("POST", "/v2/invoice", body=request.to_dict())
        return InvoiceResponse.from_dict(data)

    def cancel_invoice(self, invoice_id: str) -> None:
        """Cancel an existing invoice by ID. DELETE /v2/invoice/{id}"""
        self._do_request("DELETE", f"/v2/invoice/{invoice_id}")

    # --- Payment ---

    def get_payment(self, payment_id: str) -> PaymentDetail:
        """Retrieve payment details by payment ID. GET /v2/payment/{id}"""
        data = self._do_request("GET", f"/v2/payment/{payment_id}")
        return PaymentDetail.from_dict(data)

    def check_payment(self, request: PaymentCheckRequest) -> PaymentCheckResponse:
        """Check if a payment has been made for an invoice. POST /v2/payment/check"""
        data = self._do_request("POST", "/v2/payment/check", body=request.to_dict())
        return PaymentCheckResponse.from_dict(data)

    def list_payments(self, request: PaymentListRequest) -> PaymentListResponse:
        """Return a list of payments matching the given criteria. POST /v2/payment/list"""
        data = self._do_request("POST", "/v2/payment/list", body=request.to_dict())
        return PaymentListResponse.from_dict(data)

    def cancel_payment(
        self, payment_id: str, request: PaymentCancelRequest
    ) -> None:
        """Cancel a payment (card transactions only). DELETE /v2/payment/cancel/{id}"""
        self._do_request(
            "DELETE", f"/v2/payment/cancel/{payment_id}", body=request.to_dict()
        )

    def refund_payment(
        self, payment_id: str, request: PaymentRefundRequest
    ) -> None:
        """Refund a payment (card transactions only). DELETE /v2/payment/refund/{id}"""
        self._do_request(
            "DELETE", f"/v2/payment/refund/{payment_id}", body=request.to_dict()
        )

    # --- Ebarimt ---

    def create_ebarimt(self, request: CreateEbarimtRequest) -> EbarimtResponse:
        """Create an ebarimt (electronic tax receipt). POST /v2/ebarimt_v3/create"""
        data = self._do_request(
            "POST", "/v2/ebarimt_v3/create", body=request.to_dict()
        )
        return EbarimtResponse.from_dict(data)

    def cancel_ebarimt(self, payment_id: str) -> EbarimtResponse:
        """Cancel an ebarimt by payment ID. DELETE /v2/ebarimt_v3/{id}"""
        data = self._do_request("DELETE", f"/v2/ebarimt_v3/{payment_id}")
        return EbarimtResponse.from_dict(data)

    # --- Internal ---

    def _ensure_token(self) -> None:
        """Ensure a valid access token is available, refreshing or re-authenticating as needed."""
        with self._lock:
            now = int(time.time())
            if self._access_token and now < self._expires_at - _TOKEN_BUFFER_SECONDS:
                return
            can_refresh = (
                bool(self._refresh_token)
                and now < self._refresh_expires_at - _TOKEN_BUFFER_SECONDS
            )
            refresh_tok = self._refresh_token

        if can_refresh:
            try:
                token = self._do_refresh_token_http(refresh_tok)
                with self._lock:
                    self._store_token(token)
                return
            except Exception:
                pass  # Fall through to full auth

        token = self._get_token_request()
        with self._lock:
            self._store_token(token)

    def _store_token(self, token: TokenResponse) -> None:
        """Store token data (must be called while holding the lock)."""
        self._access_token = token.access_token
        self._refresh_token = token.refresh_token
        self._expires_at = token.expires_in
        self._refresh_expires_at = token.refresh_expires_in

    def _get_token_request(self) -> TokenResponse:
        """Perform Basic Auth token request."""
        return self._do_basic_auth_request("POST", "/v2/auth/token")

    def _do_refresh_token_http(self, refresh_tok: str) -> TokenResponse:
        """Perform token refresh HTTP call."""
        url = self._config.base_url + "/v2/auth/refresh"
        response = self._http.request(
            "POST",
            url,
            headers={"Authorization": f"Bearer {refresh_tok}"},
        )

        if response.status_code < 200 or response.status_code >= 300:
            raise QPayError.from_response(response.status_code, response.content)

        return TokenResponse.from_dict(response.json())

    def _do_request(
        self,
        method: str,
        path: str,
        *,
        body: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make an authenticated API request."""
        self._ensure_token()

        url = self._config.base_url + path
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._access_token}",
        }

        response = self._http.request(method, url, headers=headers, json=body)

        if response.status_code < 200 or response.status_code >= 300:
            raise QPayError.from_response(response.status_code, response.content)

        if response.content:
            return response.json()  # type: ignore[no-any-return]
        return {}

    def _do_basic_auth_request(self, method: str, path: str) -> TokenResponse:
        """Make a Basic Auth request for token endpoints."""
        url = self._config.base_url + path
        response = self._http.request(
            method,
            url,
            auth=(self._config.username, self._config.password),
        )

        if response.status_code < 200 or response.status_code >= 300:
            raise QPayError.from_response(response.status_code, response.content)

        return TokenResponse.from_dict(response.json())


class AsyncQPayClient:
    """Asynchronous QPay V2 API client with automatic token management.

    The client automatically obtains and refreshes access tokens as needed.
    Token management is thread-safe using asyncio locks.
    """

    def __init__(
        self,
        config: QPayConfig,
        *,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        import asyncio

        self._config = config
        self._http = http_client or httpx.AsyncClient(timeout=30.0)
        self._owns_http = http_client is None
        self._lock = asyncio.Lock()

        self._access_token = ""
        self._refresh_token = ""
        self._expires_at: int = 0
        self._refresh_expires_at: int = 0

    async def close(self) -> None:
        """Close the underlying HTTP client if it was created by this instance."""
        if self._owns_http:
            await self._http.aclose()

    async def __aenter__(self) -> AsyncQPayClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    # --- Auth ---

    async def get_token(self) -> TokenResponse:
        """Authenticate with QPay using Basic Auth and return a new token pair."""
        token = await self._get_token_request()
        async with self._lock:
            self._store_token(token)
        return token

    async def refresh_token(self) -> TokenResponse:
        """Use the current refresh token to obtain a new access token."""
        async with self._lock:
            refresh_tok = self._refresh_token
        token = await self._do_refresh_token_http(refresh_tok)
        async with self._lock:
            self._store_token(token)
        return token

    # --- Invoice ---

    async def create_invoice(self, request: CreateInvoiceRequest) -> InvoiceResponse:
        """Create a detailed invoice with full options. POST /v2/invoice"""
        data = await self._do_request("POST", "/v2/invoice", body=request.to_dict())
        return InvoiceResponse.from_dict(data)

    async def create_simple_invoice(
        self, request: CreateSimpleInvoiceRequest
    ) -> InvoiceResponse:
        """Create a simple invoice with minimal fields. POST /v2/invoice"""
        data = await self._do_request("POST", "/v2/invoice", body=request.to_dict())
        return InvoiceResponse.from_dict(data)

    async def create_ebarimt_invoice(
        self, request: CreateEbarimtInvoiceRequest
    ) -> InvoiceResponse:
        """Create an invoice with ebarimt (tax) information. POST /v2/invoice"""
        data = await self._do_request("POST", "/v2/invoice", body=request.to_dict())
        return InvoiceResponse.from_dict(data)

    async def cancel_invoice(self, invoice_id: str) -> None:
        """Cancel an existing invoice by ID. DELETE /v2/invoice/{id}"""
        await self._do_request("DELETE", f"/v2/invoice/{invoice_id}")

    # --- Payment ---

    async def get_payment(self, payment_id: str) -> PaymentDetail:
        """Retrieve payment details by payment ID. GET /v2/payment/{id}"""
        data = await self._do_request("GET", f"/v2/payment/{payment_id}")
        return PaymentDetail.from_dict(data)

    async def check_payment(
        self, request: PaymentCheckRequest
    ) -> PaymentCheckResponse:
        """Check if a payment has been made for an invoice. POST /v2/payment/check"""
        data = await self._do_request(
            "POST", "/v2/payment/check", body=request.to_dict()
        )
        return PaymentCheckResponse.from_dict(data)

    async def list_payments(
        self, request: PaymentListRequest
    ) -> PaymentListResponse:
        """Return a list of payments matching the given criteria. POST /v2/payment/list"""
        data = await self._do_request(
            "POST", "/v2/payment/list", body=request.to_dict()
        )
        return PaymentListResponse.from_dict(data)

    async def cancel_payment(
        self, payment_id: str, request: PaymentCancelRequest
    ) -> None:
        """Cancel a payment (card transactions only). DELETE /v2/payment/cancel/{id}"""
        await self._do_request(
            "DELETE", f"/v2/payment/cancel/{payment_id}", body=request.to_dict()
        )

    async def refund_payment(
        self, payment_id: str, request: PaymentRefundRequest
    ) -> None:
        """Refund a payment (card transactions only). DELETE /v2/payment/refund/{id}"""
        await self._do_request(
            "DELETE", f"/v2/payment/refund/{payment_id}", body=request.to_dict()
        )

    # --- Ebarimt ---

    async def create_ebarimt(
        self, request: CreateEbarimtRequest
    ) -> EbarimtResponse:
        """Create an ebarimt (electronic tax receipt). POST /v2/ebarimt_v3/create"""
        data = await self._do_request(
            "POST", "/v2/ebarimt_v3/create", body=request.to_dict()
        )
        return EbarimtResponse.from_dict(data)

    async def cancel_ebarimt(self, payment_id: str) -> EbarimtResponse:
        """Cancel an ebarimt by payment ID. DELETE /v2/ebarimt_v3/{id}"""
        data = await self._do_request("DELETE", f"/v2/ebarimt_v3/{payment_id}")
        return EbarimtResponse.from_dict(data)

    # --- Internal ---

    async def _ensure_token(self) -> None:
        """Ensure a valid access token is available, refreshing or re-authenticating as needed."""
        async with self._lock:
            now = int(time.time())
            if self._access_token and now < self._expires_at - _TOKEN_BUFFER_SECONDS:
                return
            can_refresh = (
                bool(self._refresh_token)
                and now < self._refresh_expires_at - _TOKEN_BUFFER_SECONDS
            )
            refresh_tok = self._refresh_token

        if can_refresh:
            try:
                token = await self._do_refresh_token_http(refresh_tok)
                async with self._lock:
                    self._store_token(token)
                return
            except Exception:
                pass  # Fall through to full auth

        token = await self._get_token_request()
        async with self._lock:
            self._store_token(token)

    def _store_token(self, token: TokenResponse) -> None:
        """Store token data (must be called while holding the lock)."""
        self._access_token = token.access_token
        self._refresh_token = token.refresh_token
        self._expires_at = token.expires_in
        self._refresh_expires_at = token.refresh_expires_in

    async def _get_token_request(self) -> TokenResponse:
        """Perform Basic Auth token request."""
        return await self._do_basic_auth_request("POST", "/v2/auth/token")

    async def _do_refresh_token_http(self, refresh_tok: str) -> TokenResponse:
        """Perform token refresh HTTP call."""
        url = self._config.base_url + "/v2/auth/refresh"
        response = await self._http.request(
            "POST",
            url,
            headers={"Authorization": f"Bearer {refresh_tok}"},
        )

        if response.status_code < 200 or response.status_code >= 300:
            raise QPayError.from_response(response.status_code, response.content)

        return TokenResponse.from_dict(response.json())

    async def _do_request(
        self,
        method: str,
        path: str,
        *,
        body: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make an authenticated API request."""
        await self._ensure_token()

        url = self._config.base_url + path
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._access_token}",
        }

        response = await self._http.request(method, url, headers=headers, json=body)

        if response.status_code < 200 or response.status_code >= 300:
            raise QPayError.from_response(response.status_code, response.content)

        if response.content:
            return response.json()  # type: ignore[no-any-return]
        return {}

    async def _do_basic_auth_request(self, method: str, path: str) -> TokenResponse:
        """Make a Basic Auth request for token endpoints."""
        url = self._config.base_url + path
        response = await self._http.request(
            method,
            url,
            auth=(self._config.username, self._config.password),
        )

        if response.status_code < 200 or response.status_code >= 300:
            raise QPayError.from_response(response.status_code, response.content)

        return TokenResponse.from_dict(response.json())
