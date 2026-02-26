"""QPay error types and error code constants."""

from __future__ import annotations


class QPayError(Exception):
    """Exception raised for QPay API errors."""

    def __init__(
        self,
        *,
        status_code: int = 0,
        code: str = "",
        message: str = "",
        raw_body: str = "",
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.raw_body = raw_body
        super().__init__(f"qpay: {code} - {message} (status {status_code})")

    @classmethod
    def from_response(cls, status_code: int, body: bytes) -> QPayError:
        """Create a QPayError from an HTTP response."""
        import json

        raw_body = body.decode("utf-8", errors="replace")
        code = ""
        message = ""

        try:
            data = json.loads(body)
            code = data.get("error", "")
            message = data.get("message", "")
        except (json.JSONDecodeError, ValueError):
            pass

        if not code:
            from http import HTTPStatus

            try:
                code = HTTPStatus(status_code).phrase
            except ValueError:
                code = str(status_code)

        if not message:
            message = raw_body

        return cls(
            status_code=status_code,
            code=code,
            message=message,
            raw_body=raw_body,
        )


def is_qpay_error(err: BaseException | None) -> QPayError | None:
    """Check if an exception is a QPayError and return it, or None."""
    if isinstance(err, QPayError):
        return err
    return None


# Error code constants
ERR_ACCOUNT_BANK_DUPLICATED = "ACCOUNT_BANK_DUPLICATED"
ERR_ACCOUNT_SELECTION_INVALID = "ACCOUNT_SELECTION_INVALID"
ERR_AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
ERR_BANK_ACCOUNT_NOT_FOUND = "BANK_ACCOUNT_NOTFOUND"
ERR_BANK_MCC_ALREADY_ADDED = "BANK_MCC_ALREADY_ADDED"
ERR_BANK_MCC_NOT_FOUND = "BANK_MCC_NOT_FOUND"
ERR_CARD_TERMINAL_NOT_FOUND = "CARD_TERMINAL_NOTFOUND"
ERR_CLIENT_NOT_FOUND = "CLIENT_NOTFOUND"
ERR_CLIENT_USERNAME_DUPLICATED = "CLIENT_USERNAME_DUPLICATED"
ERR_CUSTOMER_DUPLICATE = "CUSTOMER_DUPLICATE"
ERR_CUSTOMER_NOT_FOUND = "CUSTOMER_NOTFOUND"
ERR_CUSTOMER_REGISTER_INVALID = "CUSTOMER_REGISTER_INVALID"
ERR_EBARIMT_CANCEL_NOT_SUPPORTED = "EBARIMT_CANCEL_NOTSUPPERDED"
ERR_EBARIMT_NOT_REGISTERED = "EBARIMT_NOT_REGISTERED"
ERR_EBARIMT_QR_CODE_INVALID = "EBARIMT_QR_CODE_INVALID"
ERR_INFORM_NOT_FOUND = "INFORM_NOTFOUND"
ERR_INPUT_CODE_REGISTERED = "INPUT_CODE_REGISTERED"
ERR_INPUT_NOT_FOUND = "INPUT_NOTFOUND"
ERR_INVALID_AMOUNT = "INVALID_AMOUNT"
ERR_INVALID_OBJECT_TYPE = "INVALID_OBJECT_TYPE"
ERR_INVOICE_ALREADY_CANCELED = "INVOICE_ALREADY_CANCELED"
ERR_INVOICE_CODE_INVALID = "INVOICE_CODE_INVALID"
ERR_INVOICE_CODE_REGISTERED = "INVOICE_CODE_REGISTERED"
ERR_INVOICE_LINE_REQUIRED = "INVOICE_LINE_REQUIRED"
ERR_INVOICE_NOT_FOUND = "INVOICE_NOTFOUND"
ERR_INVOICE_PAID = "INVOICE_PAID"
ERR_INVOICE_RECEIVER_DATA_ADDRESS_REQUIRED = "INVOICE_RECEIVER_DATA_ADDRESS_REQUIRED"
ERR_INVOICE_RECEIVER_DATA_EMAIL_REQUIRED = "INVOICE_RECEIVER_DATA_EMAIL_REQUIRED"
ERR_INVOICE_RECEIVER_DATA_PHONE_REQUIRED = "INVOICE_RECEIVER_DATA_PHONE_REQUIRED"
ERR_INVOICE_RECEIVER_DATA_REQUIRED = "INVOICE_RECEIVER_DATA_REQUIRED"
ERR_MAX_AMOUNT_ERR = "MAX_AMOUNT_ERR"
ERR_MCC_NOT_FOUND = "MCC_NOTFOUND"
ERR_MERCHANT_ALREADY_REGISTERED = "MERCHANT_ALREADY_REGISTERED"
ERR_MERCHANT_INACTIVE = "MERCHANT_INACTIVE"
ERR_MERCHANT_NOT_FOUND = "MERCHANT_NOTFOUND"
ERR_MIN_AMOUNT_ERR = "MIN_AMOUNT_ERR"
ERR_NO_CREDENTIALS = "NO_CREDENDIALS"
ERR_OBJECT_DATA_ERROR = "OBJECT_DATA_ERROR"
ERR_P2P_TERMINAL_NOT_FOUND = "P2P_TERMINAL_NOTFOUND"
ERR_PAYMENT_ALREADY_CANCELED = "PAYMENT_ALREADY_CANCELED"
ERR_PAYMENT_NOT_PAID = "PAYMENT_NOT_PAID"
ERR_PAYMENT_NOT_FOUND = "PAYMENT_NOTFOUND"
ERR_PERMISSION_DENIED = "PERMISSION_DENIED"
ERR_QR_ACCOUNT_INACTIVE = "QRACCOUNT_INACTIVE"
ERR_QR_ACCOUNT_NOT_FOUND = "QRACCOUNT_NOTFOUND"
ERR_QR_CODE_NOT_FOUND = "QRCODE_NOTFOUND"
ERR_QR_CODE_USED = "QRCODE_USED"
ERR_SENDER_BRANCH_DATA_REQUIRED = "SENDER_BRANCH_DATA_REQUIRED"
ERR_TAX_LINE_REQUIRED = "TAX_LINE_REQUIRED"
ERR_TAX_PRODUCT_CODE_REQUIRED = "TAX_PRODUCT_CODE_REQUIRED"
ERR_TRANSACTION_NOT_APPROVED = "TRANSACTION_NOT_APPROVED"
ERR_TRANSACTION_REQUIRED = "TRANSACTION_REQUIRED"
