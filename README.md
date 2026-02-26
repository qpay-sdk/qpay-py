# qpay-py

[![PyPI version](https://img.shields.io/pypi/v/qpay-py.svg)](https://pypi.org/project/qpay-py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Python SDK for the QPay V2 API. Provides both synchronous and asynchronous clients with automatic token management, typed request/response objects, and comprehensive error handling.

## Installation

```bash
pip install qpay-py
```

## Quick Start

### Synchronous

```python
from qpay import QPayClient, QPayConfig, CreateSimpleInvoiceRequest

config = QPayConfig(
    base_url="https://merchant.qpay.mn",
    username="your_username",
    password="your_password",
    invoice_code="YOUR_INVOICE_CODE",
    callback_url="https://yoursite.com/callback",
)

with QPayClient(config) as client:
    invoice = client.create_simple_invoice(
        CreateSimpleInvoiceRequest(
            invoice_code=config.invoice_code,
            sender_invoice_no="ORDER-001",
            invoice_receiver_code="terminal",
            invoice_description="Payment for Order #001",
            amount=50000.0,
            callback_url=config.callback_url,
        )
    )
    print(f"Invoice ID: {invoice.invoice_id}")
    print(f"QR Image:   {invoice.qr_image}")
    print(f"Short URL:  {invoice.qpay_short_url}")
```

### Asynchronous

```python
import asyncio
from qpay import AsyncQPayClient, QPayConfig, CreateSimpleInvoiceRequest

config = QPayConfig(
    base_url="https://merchant.qpay.mn",
    username="your_username",
    password="your_password",
    invoice_code="YOUR_INVOICE_CODE",
    callback_url="https://yoursite.com/callback",
)

async def main():
    async with AsyncQPayClient(config) as client:
        invoice = await client.create_simple_invoice(
            CreateSimpleInvoiceRequest(
                invoice_code=config.invoice_code,
                sender_invoice_no="ORDER-001",
                invoice_receiver_code="terminal",
                invoice_description="Payment for Order #001",
                amount=50000.0,
                callback_url=config.callback_url,
            )
        )
        print(f"Invoice ID: {invoice.invoice_id}")

asyncio.run(main())
```

## Configuration

### Direct construction

```python
from qpay import QPayConfig

config = QPayConfig(
    base_url="https://merchant.qpay.mn",
    username="your_username",
    password="your_password",
    invoice_code="YOUR_INVOICE_CODE",
    callback_url="https://yoursite.com/callback",
)
```

### From environment variables

Set the following environment variables:

| Variable | Description |
|---|---|
| `QPAY_BASE_URL` | QPay API base URL |
| `QPAY_USERNAME` | QPay merchant username |
| `QPAY_PASSWORD` | QPay merchant password |
| `QPAY_INVOICE_CODE` | Default invoice code |
| `QPAY_CALLBACK_URL` | Payment callback URL |

```python
from qpay import QPayConfig

config = QPayConfig.from_env()
```

A `ValueError` is raised if any required variable is missing or empty.

## Usage

All examples below use the synchronous `QPayClient`. The `AsyncQPayClient` has identical methods, but each returns a coroutine that must be `await`ed.

### Authentication

Token management is automatic. The client obtains a token on the first API call and refreshes it transparently when it expires. You can also manage tokens manually:

```python
# Explicitly get a new token
token = client.get_token()
print(token.access_token)

# Explicitly refresh
token = client.refresh_token()
```

### Create Invoice (full options)

```python
from qpay import (
    CreateInvoiceRequest,
    InvoiceLine,
    InvoiceReceiverData,
    SenderBranchData,
    TaxEntry,
    Transaction,
    Account,
)

invoice = client.create_invoice(
    CreateInvoiceRequest(
        invoice_code="YOUR_CODE",
        sender_invoice_no="INV-100",
        invoice_receiver_code="terminal",
        invoice_description="Detailed invoice",
        amount=100000.0,
        callback_url="https://yoursite.com/callback",
        invoice_receiver_data=InvoiceReceiverData(
            register="AA12345678",
            name="Customer Name",
            email="customer@example.com",
            phone="99001122",
        ),
        lines=[
            InvoiceLine(
                tax_product_code="1234567",
                line_description="Widget",
                line_quantity="2",
                line_unit_price="50000",
            ),
        ],
    )
)
```

### Create Simple Invoice

```python
from qpay import CreateSimpleInvoiceRequest

invoice = client.create_simple_invoice(
    CreateSimpleInvoiceRequest(
        invoice_code="YOUR_CODE",
        sender_invoice_no="INV-101",
        invoice_receiver_code="terminal",
        invoice_description="Simple invoice",
        amount=10000.0,
        callback_url="https://yoursite.com/callback",
    )
)
```

### Create Ebarimt Invoice

```python
from qpay import CreateEbarimtInvoiceRequest, EbarimtInvoiceLine

invoice = client.create_ebarimt_invoice(
    CreateEbarimtInvoiceRequest(
        invoice_code="YOUR_CODE",
        sender_invoice_no="INV-102",
        invoice_receiver_code="terminal",
        invoice_description="Ebarimt invoice",
        tax_type="1",
        district_code="23",
        callback_url="https://yoursite.com/callback",
        lines=[
            EbarimtInvoiceLine(
                tax_product_code="1234567",
                line_description="Product A",
                line_quantity="1",
                line_unit_price="10000",
            ),
        ],
    )
)
```

### Cancel Invoice

```python
client.cancel_invoice("invoice-id-here")
```

### Get Payment

```python
payment = client.get_payment("payment-id-here")
print(f"Status: {payment.payment_status}")
print(f"Amount: {payment.payment_amount} {payment.payment_currency}")
```

### Check Payment

```python
from qpay import PaymentCheckRequest, Offset

result = client.check_payment(
    PaymentCheckRequest(
        object_type="INVOICE",
        object_id="invoice-id-here",
        offset=Offset(page_number=1, page_limit=10),
    )
)
print(f"Paid: {result.paid_amount}")
for row in result.rows:
    print(f"  Payment {row.payment_id}: {row.payment_status}")
```

### List Payments

```python
from qpay import PaymentListRequest, Offset

result = client.list_payments(
    PaymentListRequest(
        object_type="INVOICE",
        object_id="invoice-id-here",
        start_date="2024-01-01",
        end_date="2024-12-31",
        offset=Offset(page_number=1, page_limit=20),
    )
)
print(f"Total: {result.count}")
for item in result.rows:
    print(f"  {item.payment_id} - {item.payment_amount} {item.payment_currency}")
```

### Cancel Payment

```python
from qpay import PaymentCancelRequest

client.cancel_payment(
    "payment-id-here",
    PaymentCancelRequest(
        callback_url="https://yoursite.com/callback",
        note="Customer requested cancellation",
    ),
)
```

### Refund Payment

```python
from qpay import PaymentRefundRequest

client.refund_payment(
    "payment-id-here",
    PaymentRefundRequest(
        callback_url="https://yoursite.com/callback",
        note="Refund for defective product",
    ),
)
```

### Create Ebarimt

```python
from qpay import CreateEbarimtRequest

ebarimt = client.create_ebarimt(
    CreateEbarimtRequest(
        payment_id="payment-id-here",
        ebarimt_receiver_type="83",
    )
)
print(f"Lottery: {ebarimt.ebarimt_lottery}")
print(f"QR Data: {ebarimt.ebarimt_qr_data}")
```

### Cancel Ebarimt

```python
ebarimt = client.cancel_ebarimt("payment-id-here")
print(f"Status: {ebarimt.barimt_status}")
```

## Error Handling

All API errors raise `QPayError` with structured information:

```python
from qpay import QPayError, is_qpay_error

try:
    client.cancel_invoice("nonexistent-id")
except QPayError as e:
    print(f"Status: {e.status_code}")  # e.g. 404
    print(f"Code:   {e.code}")         # e.g. "INVOICE_NOTFOUND"
    print(f"Msg:    {e.message}")      # e.g. "Invoice not found"
    print(f"Raw:    {e.raw_body}")     # full response body
```

The `is_qpay_error()` helper returns the `QPayError` if the argument is one, or `None` otherwise:

```python
try:
    client.get_payment("bad-id")
except Exception as e:
    qpay_err = is_qpay_error(e)
    if qpay_err:
        print(f"QPay error: {qpay_err.code}")
    else:
        raise
```

### Error code constants

The SDK exports named constants for all known QPay error codes, so you can match against them without hardcoding strings:

```python
from qpay import ERR_INVOICE_NOT_FOUND, ERR_PAYMENT_ALREADY_CANCELED, QPayError

try:
    client.cancel_invoice("some-id")
except QPayError as e:
    if e.code == ERR_INVOICE_NOT_FOUND:
        print("Invoice does not exist")
    elif e.code == ERR_PAYMENT_ALREADY_CANCELED:
        print("Already canceled")
    else:
        raise
```

## Async Patterns

### With FastAPI

```python
from fastapi import FastAPI, HTTPException
from qpay import AsyncQPayClient, QPayConfig, QPayError, CreateSimpleInvoiceRequest

app = FastAPI()
config = QPayConfig.from_env()
qpay = AsyncQPayClient(config)

@app.on_event("shutdown")
async def shutdown():
    await qpay.close()

@app.post("/create-invoice")
async def create_invoice(amount: float, description: str):
    try:
        invoice = await qpay.create_simple_invoice(
            CreateSimpleInvoiceRequest(
                invoice_code=config.invoice_code,
                sender_invoice_no="ORDER-001",
                invoice_receiver_code="terminal",
                invoice_description=description,
                amount=amount,
                callback_url=config.callback_url,
            )
        )
        return {"invoice_id": invoice.invoice_id, "qr_image": invoice.qr_image}
    except QPayError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
```

### With aiohttp or any async framework

```python
async def process_payment():
    async with AsyncQPayClient(config) as client:
        invoice = await client.create_simple_invoice(...)
        # ... do work ...
        check = await client.check_payment(...)
        return check.paid_amount > 0
```

## API Reference

### Clients

| Class | Description |
|---|---|
| `QPayClient` | Synchronous client. Use with `with` statement or call `.close()`. |
| `AsyncQPayClient` | Asynchronous client. Use with `async with` or call `await .close()`. |

### Client Methods

| Method | Returns | Description |
|---|---|---|
| `get_token()` | `TokenResponse` | Authenticate and get a new token pair |
| `refresh_token()` | `TokenResponse` | Refresh the current access token |
| `create_invoice(req)` | `InvoiceResponse` | Create a detailed invoice |
| `create_simple_invoice(req)` | `InvoiceResponse` | Create a simple invoice |
| `create_ebarimt_invoice(req)` | `InvoiceResponse` | Create an invoice with ebarimt |
| `cancel_invoice(id)` | `None` | Cancel an invoice |
| `get_payment(id)` | `PaymentDetail` | Get payment details |
| `check_payment(req)` | `PaymentCheckResponse` | Check payment status |
| `list_payments(req)` | `PaymentListResponse` | List payments |
| `cancel_payment(id, req)` | `None` | Cancel a payment |
| `refund_payment(id, req)` | `None` | Refund a payment |
| `create_ebarimt(req)` | `EbarimtResponse` | Create an ebarimt receipt |
| `cancel_ebarimt(id)` | `EbarimtResponse` | Cancel an ebarimt receipt |

### Configuration

| Class | Description |
|---|---|
| `QPayConfig` | Configuration dataclass with `base_url`, `username`, `password`, `invoice_code`, `callback_url` |
| `QPayConfig.from_env()` | Load config from environment variables |

### Request Types

| Type | Used By |
|---|---|
| `CreateInvoiceRequest` | `create_invoice()` |
| `CreateSimpleInvoiceRequest` | `create_simple_invoice()` |
| `CreateEbarimtInvoiceRequest` | `create_ebarimt_invoice()` |
| `PaymentCheckRequest` | `check_payment()` |
| `PaymentListRequest` | `list_payments()` |
| `PaymentCancelRequest` | `cancel_payment()` |
| `PaymentRefundRequest` | `refund_payment()` |
| `CreateEbarimtRequest` | `create_ebarimt()` |

### Response Types

| Type | Description |
|---|---|
| `TokenResponse` | Access/refresh token pair |
| `InvoiceResponse` | Invoice ID, QR code, deeplinks |
| `PaymentDetail` | Full payment information |
| `PaymentCheckResponse` | Payment check result with rows |
| `PaymentListResponse` | Paginated payment list |
| `EbarimtResponse` | Ebarimt receipt details |

### Supporting Types

`Offset`, `Deeplink`, `Account`, `Address`, `InvoiceLine`, `EbarimtInvoiceLine`, `InvoiceReceiverData`, `SenderBranchData`, `SenderStaffData`, `TaxEntry`, `Transaction`, `CardTransaction`, `P2PTransaction`, `PaymentCheckRow`, `PaymentListItem`, `EbarimtItem`, `EbarimtHistory`

### Error Handling

| Symbol | Description |
|---|---|
| `QPayError` | Exception with `status_code`, `code`, `message`, `raw_body` |
| `is_qpay_error(err)` | Returns `QPayError` if `err` is one, else `None` |
| `ERR_*` constants | Named constants for all QPay error codes |

## License

MIT
