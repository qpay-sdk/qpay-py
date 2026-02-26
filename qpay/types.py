"""QPay request and response types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


# --- Auth ---


@dataclass
class TokenResponse:
    """Token response from QPay auth endpoints."""

    token_type: str = ""
    refresh_expires_in: int = 0
    refresh_token: str = ""
    access_token: str = ""
    expires_in: int = 0
    scope: str = ""
    not_before_policy: str = ""
    session_state: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TokenResponse:
        return cls(
            token_type=data.get("token_type", ""),
            refresh_expires_in=data.get("refresh_expires_in", 0),
            refresh_token=data.get("refresh_token", ""),
            access_token=data.get("access_token", ""),
            expires_in=data.get("expires_in", 0),
            scope=data.get("scope", ""),
            not_before_policy=data.get("not-before-policy", ""),
            session_state=data.get("session_state", ""),
        )


# --- Common nested types ---


@dataclass
class Address:
    """Address information."""

    city: str = ""
    district: str = ""
    street: str = ""
    building: str = ""
    address: str = ""
    zipcode: str = ""
    longitude: str = ""
    latitude: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.city:
            d["city"] = self.city
        if self.district:
            d["district"] = self.district
        if self.street:
            d["street"] = self.street
        if self.building:
            d["building"] = self.building
        if self.address:
            d["address"] = self.address
        if self.zipcode:
            d["zipcode"] = self.zipcode
        if self.longitude:
            d["longitude"] = self.longitude
        if self.latitude:
            d["latitude"] = self.latitude
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Address | None:
        if not data:
            return None
        return cls(
            city=data.get("city", ""),
            district=data.get("district", ""),
            street=data.get("street", ""),
            building=data.get("building", ""),
            address=data.get("address", ""),
            zipcode=data.get("zipcode", ""),
            longitude=data.get("longitude", ""),
            latitude=data.get("latitude", ""),
        )


@dataclass
class SenderBranchData:
    """Sender branch data for invoices."""

    register: str = ""
    name: str = ""
    email: str = ""
    phone: str = ""
    address: Optional[Address] = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.register:
            d["register"] = self.register
        if self.name:
            d["name"] = self.name
        if self.email:
            d["email"] = self.email
        if self.phone:
            d["phone"] = self.phone
        if self.address:
            d["address"] = self.address.to_dict()
        return d


@dataclass
class SenderStaffData:
    """Sender staff data for invoices."""

    name: str = ""
    email: str = ""
    phone: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.name:
            d["name"] = self.name
        if self.email:
            d["email"] = self.email
        if self.phone:
            d["phone"] = self.phone
        return d


@dataclass
class InvoiceReceiverData:
    """Invoice receiver data."""

    register: str = ""
    name: str = ""
    email: str = ""
    phone: str = ""
    address: Optional[Address] = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.register:
            d["register"] = self.register
        if self.name:
            d["name"] = self.name
        if self.email:
            d["email"] = self.email
        if self.phone:
            d["phone"] = self.phone
        if self.address:
            d["address"] = self.address.to_dict()
        return d


@dataclass
class Account:
    """Bank account information."""

    account_bank_code: str = ""
    account_number: str = ""
    iban_number: str = ""
    account_name: str = ""
    account_currency: str = ""
    is_default: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "account_bank_code": self.account_bank_code,
            "account_number": self.account_number,
            "iban_number": self.iban_number,
            "account_name": self.account_name,
            "account_currency": self.account_currency,
            "is_default": self.is_default,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Account:
        return cls(
            account_bank_code=data.get("account_bank_code", ""),
            account_number=data.get("account_number", ""),
            iban_number=data.get("iban_number", ""),
            account_name=data.get("account_name", ""),
            account_currency=data.get("account_currency", ""),
            is_default=data.get("is_default", False),
        )


@dataclass
class TaxEntry:
    """Tax, discount, or surcharge entry."""

    tax_code: str = ""
    discount_code: str = ""
    surcharge_code: str = ""
    description: str = ""
    amount: float = 0.0
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"description": self.description, "amount": self.amount}
        if self.tax_code:
            d["tax_code"] = self.tax_code
        if self.discount_code:
            d["discount_code"] = self.discount_code
        if self.surcharge_code:
            d["surcharge_code"] = self.surcharge_code
        if self.note:
            d["note"] = self.note
        return d


@dataclass
class Transaction:
    """Transaction within an invoice."""

    description: str = ""
    amount: str = ""
    accounts: list[Account] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "description": self.description,
            "amount": self.amount,
        }
        if self.accounts:
            d["accounts"] = [a.to_dict() for a in self.accounts]
        return d


@dataclass
class InvoiceLine:
    """Line item in an invoice."""

    tax_product_code: str = ""
    line_description: str = ""
    line_quantity: str = ""
    line_unit_price: str = ""
    note: str = ""
    discounts: list[TaxEntry] = field(default_factory=list)
    surcharges: list[TaxEntry] = field(default_factory=list)
    taxes: list[TaxEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "line_description": self.line_description,
            "line_quantity": self.line_quantity,
            "line_unit_price": self.line_unit_price,
        }
        if self.tax_product_code:
            d["tax_product_code"] = self.tax_product_code
        if self.note:
            d["note"] = self.note
        if self.discounts:
            d["discounts"] = [e.to_dict() for e in self.discounts]
        if self.surcharges:
            d["surcharges"] = [e.to_dict() for e in self.surcharges]
        if self.taxes:
            d["taxes"] = [e.to_dict() for e in self.taxes]
        return d


@dataclass
class EbarimtInvoiceLine:
    """Line item in an ebarimt invoice."""

    tax_product_code: str = ""
    line_description: str = ""
    barcode: str = ""
    line_quantity: str = ""
    line_unit_price: str = ""
    note: str = ""
    classification_code: str = ""
    taxes: list[TaxEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "line_description": self.line_description,
            "line_quantity": self.line_quantity,
            "line_unit_price": self.line_unit_price,
        }
        if self.tax_product_code:
            d["tax_product_code"] = self.tax_product_code
        if self.barcode:
            d["barcode"] = self.barcode
        if self.note:
            d["note"] = self.note
        if self.classification_code:
            d["classification_code"] = self.classification_code
        if self.taxes:
            d["taxes"] = [e.to_dict() for e in self.taxes]
        return d


@dataclass
class Deeplink:
    """Payment deeplink for bank apps."""

    name: str = ""
    description: str = ""
    logo: str = ""
    link: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Deeplink:
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            logo=data.get("logo", ""),
            link=data.get("link", ""),
        )


# --- Invoice ---


@dataclass
class CreateInvoiceRequest:
    """Request to create a detailed invoice."""

    invoice_code: str
    sender_invoice_no: str
    invoice_receiver_code: str
    invoice_description: str
    amount: float
    callback_url: str
    sender_branch_code: str = ""
    sender_branch_data: Optional[SenderBranchData] = None
    sender_staff_data: Optional[SenderStaffData] = None
    sender_staff_code: str = ""
    invoice_receiver_data: Optional[InvoiceReceiverData] = None
    enable_expiry: Optional[str] = None
    allow_partial: Optional[bool] = None
    minimum_amount: Optional[float] = None
    allow_exceed: Optional[bool] = None
    maximum_amount: Optional[float] = None
    sender_terminal_code: Optional[str] = None
    sender_terminal_data: Any = None
    allow_subscribe: Optional[bool] = None
    subscription_interval: str = ""
    subscription_webhook: str = ""
    note: Optional[str] = None
    transactions: list[Transaction] = field(default_factory=list)
    lines: list[InvoiceLine] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "invoice_code": self.invoice_code,
            "sender_invoice_no": self.sender_invoice_no,
            "invoice_receiver_code": self.invoice_receiver_code,
            "invoice_description": self.invoice_description,
            "amount": self.amount,
            "callback_url": self.callback_url,
        }
        if self.sender_branch_code:
            d["sender_branch_code"] = self.sender_branch_code
        if self.sender_branch_data:
            d["sender_branch_data"] = self.sender_branch_data.to_dict()
        if self.sender_staff_data:
            d["sender_staff_data"] = self.sender_staff_data.to_dict()
        if self.sender_staff_code:
            d["sender_staff_code"] = self.sender_staff_code
        if self.invoice_receiver_data:
            d["invoice_receiver_data"] = self.invoice_receiver_data.to_dict()
        if self.enable_expiry is not None:
            d["enable_expiry"] = self.enable_expiry
        if self.allow_partial is not None:
            d["allow_partial"] = self.allow_partial
        if self.minimum_amount is not None:
            d["minimum_amount"] = self.minimum_amount
        if self.allow_exceed is not None:
            d["allow_exceed"] = self.allow_exceed
        if self.maximum_amount is not None:
            d["maximum_amount"] = self.maximum_amount
        if self.sender_terminal_code is not None:
            d["sender_terminal_code"] = self.sender_terminal_code
        if self.sender_terminal_data is not None:
            d["sender_terminal_data"] = self.sender_terminal_data
        if self.allow_subscribe is not None:
            d["allow_subscribe"] = self.allow_subscribe
        if self.subscription_interval:
            d["subscription_interval"] = self.subscription_interval
        if self.subscription_webhook:
            d["subscription_webhook"] = self.subscription_webhook
        if self.note is not None:
            d["note"] = self.note
        if self.transactions:
            d["transactions"] = [t.to_dict() for t in self.transactions]
        if self.lines:
            d["lines"] = [ln.to_dict() for ln in self.lines]
        return d


@dataclass
class CreateSimpleInvoiceRequest:
    """Request to create a simple invoice with minimal fields."""

    invoice_code: str
    sender_invoice_no: str
    invoice_receiver_code: str
    invoice_description: str
    amount: float
    callback_url: str
    sender_branch_code: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "invoice_code": self.invoice_code,
            "sender_invoice_no": self.sender_invoice_no,
            "invoice_receiver_code": self.invoice_receiver_code,
            "invoice_description": self.invoice_description,
            "amount": self.amount,
            "callback_url": self.callback_url,
        }
        if self.sender_branch_code:
            d["sender_branch_code"] = self.sender_branch_code
        return d


@dataclass
class CreateEbarimtInvoiceRequest:
    """Request to create an invoice with ebarimt (tax) information."""

    invoice_code: str
    sender_invoice_no: str
    invoice_receiver_code: str
    invoice_description: str
    tax_type: str
    district_code: str
    callback_url: str
    lines: list[EbarimtInvoiceLine]
    sender_branch_code: str = ""
    sender_staff_data: Optional[SenderStaffData] = None
    sender_staff_code: str = ""
    invoice_receiver_data: Optional[InvoiceReceiverData] = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "invoice_code": self.invoice_code,
            "sender_invoice_no": self.sender_invoice_no,
            "invoice_receiver_code": self.invoice_receiver_code,
            "invoice_description": self.invoice_description,
            "tax_type": self.tax_type,
            "district_code": self.district_code,
            "callback_url": self.callback_url,
            "lines": [ln.to_dict() for ln in self.lines],
        }
        if self.sender_branch_code:
            d["sender_branch_code"] = self.sender_branch_code
        if self.sender_staff_data:
            d["sender_staff_data"] = self.sender_staff_data.to_dict()
        if self.sender_staff_code:
            d["sender_staff_code"] = self.sender_staff_code
        if self.invoice_receiver_data:
            d["invoice_receiver_data"] = self.invoice_receiver_data.to_dict()
        return d


@dataclass
class InvoiceResponse:
    """Response from creating an invoice."""

    invoice_id: str = ""
    qr_text: str = ""
    qr_image: str = ""
    qpay_short_url: str = ""
    urls: list[Deeplink] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InvoiceResponse:
        return cls(
            invoice_id=data.get("invoice_id", ""),
            qr_text=data.get("qr_text", ""),
            qr_image=data.get("qr_image", ""),
            qpay_short_url=data.get("qPay_shortUrl", ""),
            urls=[Deeplink.from_dict(u) for u in data.get("urls", [])],
        )


# --- Payment ---


@dataclass
class Offset:
    """Pagination offset."""

    page_number: int = 0
    page_limit: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_number": self.page_number,
            "page_limit": self.page_limit,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> Offset | None:
        if not data:
            return None
        return cls(
            page_number=data.get("page_number", 0),
            page_limit=data.get("page_limit", 0),
        )


@dataclass
class PaymentCheckRequest:
    """Request to check payment status."""

    object_type: str
    object_id: str
    offset: Optional[Offset] = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "object_type": self.object_type,
            "object_id": self.object_id,
        }
        if self.offset:
            d["offset"] = self.offset.to_dict()
        return d


@dataclass
class CardTransaction:
    """Card transaction details."""

    card_merchant_code: str = ""
    card_terminal_code: str = ""
    card_number: str = ""
    card_type: str = ""
    is_cross_border: bool = False
    amount: str = ""
    transaction_amount: str = ""
    currency: str = ""
    transaction_currency: str = ""
    date: str = ""
    transaction_date: str = ""
    status: str = ""
    transaction_status: str = ""
    settlement_status: str = ""
    settlement_status_date: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CardTransaction:
        return cls(
            card_merchant_code=data.get("card_merchant_code", ""),
            card_terminal_code=data.get("card_terminal_code", ""),
            card_number=data.get("card_number", ""),
            card_type=data.get("card_type", ""),
            is_cross_border=data.get("is_cross_border", False),
            amount=data.get("amount", ""),
            transaction_amount=data.get("transaction_amount", ""),
            currency=data.get("currency", ""),
            transaction_currency=data.get("transaction_currency", ""),
            date=data.get("date", ""),
            transaction_date=data.get("transaction_date", ""),
            status=data.get("status", ""),
            transaction_status=data.get("transaction_status", ""),
            settlement_status=data.get("settlement_status", ""),
            settlement_status_date=data.get("settlement_status_date", ""),
        )


@dataclass
class P2PTransaction:
    """P2P transaction details."""

    transaction_bank_code: str = ""
    account_bank_code: str = ""
    account_bank_name: str = ""
    account_number: str = ""
    status: str = ""
    amount: str = ""
    currency: str = ""
    settlement_status: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> P2PTransaction:
        return cls(
            transaction_bank_code=data.get("transaction_bank_code", ""),
            account_bank_code=data.get("account_bank_code", ""),
            account_bank_name=data.get("account_bank_name", ""),
            account_number=data.get("account_number", ""),
            status=data.get("status", ""),
            amount=data.get("amount", ""),
            currency=data.get("currency", ""),
            settlement_status=data.get("settlement_status", ""),
        )


@dataclass
class PaymentCheckRow:
    """Row in a payment check response."""

    payment_id: str = ""
    payment_status: str = ""
    payment_amount: str = ""
    trx_fee: str = ""
    payment_currency: str = ""
    payment_wallet: str = ""
    payment_type: str = ""
    next_payment_date: Optional[str] = None
    next_payment_datetime: Optional[str] = None
    card_transactions: list[CardTransaction] = field(default_factory=list)
    p2p_transactions: list[P2PTransaction] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PaymentCheckRow:
        return cls(
            payment_id=data.get("payment_id", ""),
            payment_status=data.get("payment_status", ""),
            payment_amount=data.get("payment_amount", ""),
            trx_fee=data.get("trx_fee", ""),
            payment_currency=data.get("payment_currency", ""),
            payment_wallet=data.get("payment_wallet", ""),
            payment_type=data.get("payment_type", ""),
            next_payment_date=data.get("next_payment_date"),
            next_payment_datetime=data.get("next_payment_datetime"),
            card_transactions=[
                CardTransaction.from_dict(ct)
                for ct in data.get("card_transactions", [])
            ],
            p2p_transactions=[
                P2PTransaction.from_dict(pt)
                for pt in data.get("p2p_transactions", [])
            ],
        )


@dataclass
class PaymentCheckResponse:
    """Response from checking payment status."""

    count: int = 0
    paid_amount: float = 0.0
    rows: list[PaymentCheckRow] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PaymentCheckResponse:
        return cls(
            count=data.get("count", 0),
            paid_amount=data.get("paid_amount", 0.0),
            rows=[PaymentCheckRow.from_dict(r) for r in data.get("rows", [])],
        )


@dataclass
class PaymentDetail:
    """Detailed payment information."""

    payment_id: str = ""
    payment_status: str = ""
    payment_fee: str = ""
    payment_amount: str = ""
    payment_currency: str = ""
    payment_date: str = ""
    payment_wallet: str = ""
    transaction_type: str = ""
    object_type: str = ""
    object_id: str = ""
    next_payment_date: Optional[str] = None
    next_payment_datetime: Optional[str] = None
    card_transactions: list[CardTransaction] = field(default_factory=list)
    p2p_transactions: list[P2PTransaction] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PaymentDetail:
        return cls(
            payment_id=data.get("payment_id", ""),
            payment_status=data.get("payment_status", ""),
            payment_fee=data.get("payment_fee", ""),
            payment_amount=data.get("payment_amount", ""),
            payment_currency=data.get("payment_currency", ""),
            payment_date=data.get("payment_date", ""),
            payment_wallet=data.get("payment_wallet", ""),
            transaction_type=data.get("transaction_type", ""),
            object_type=data.get("object_type", ""),
            object_id=data.get("object_id", ""),
            next_payment_date=data.get("next_payment_date"),
            next_payment_datetime=data.get("next_payment_datetime"),
            card_transactions=[
                CardTransaction.from_dict(ct)
                for ct in data.get("card_transactions", [])
            ],
            p2p_transactions=[
                P2PTransaction.from_dict(pt)
                for pt in data.get("p2p_transactions", [])
            ],
        )


@dataclass
class PaymentListRequest:
    """Request to list payments."""

    object_type: str
    object_id: str
    start_date: str
    end_date: str
    offset: Offset

    def to_dict(self) -> dict[str, Any]:
        return {
            "object_type": self.object_type,
            "object_id": self.object_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "offset": self.offset.to_dict(),
        }


@dataclass
class PaymentListItem:
    """Item in a payment list response."""

    payment_id: str = ""
    payment_date: str = ""
    payment_status: str = ""
    payment_fee: str = ""
    payment_amount: str = ""
    payment_currency: str = ""
    payment_wallet: str = ""
    payment_name: str = ""
    payment_description: str = ""
    qr_code: str = ""
    paid_by: str = ""
    object_type: str = ""
    object_id: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PaymentListItem:
        return cls(
            payment_id=data.get("payment_id", ""),
            payment_date=data.get("payment_date", ""),
            payment_status=data.get("payment_status", ""),
            payment_fee=data.get("payment_fee", ""),
            payment_amount=data.get("payment_amount", ""),
            payment_currency=data.get("payment_currency", ""),
            payment_wallet=data.get("payment_wallet", ""),
            payment_name=data.get("payment_name", ""),
            payment_description=data.get("payment_description", ""),
            qr_code=data.get("qr_code", ""),
            paid_by=data.get("paid_by", ""),
            object_type=data.get("object_type", ""),
            object_id=data.get("object_id", ""),
        )


@dataclass
class PaymentListResponse:
    """Response from listing payments."""

    count: int = 0
    rows: list[PaymentListItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PaymentListResponse:
        return cls(
            count=data.get("count", 0),
            rows=[PaymentListItem.from_dict(r) for r in data.get("rows", [])],
        )


@dataclass
class PaymentCancelRequest:
    """Request to cancel a payment."""

    callback_url: str = ""
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.callback_url:
            d["callback_url"] = self.callback_url
        if self.note:
            d["note"] = self.note
        return d


@dataclass
class PaymentRefundRequest:
    """Request to refund a payment."""

    callback_url: str = ""
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.callback_url:
            d["callback_url"] = self.callback_url
        if self.note:
            d["note"] = self.note
        return d


# --- Ebarimt ---


@dataclass
class CreateEbarimtRequest:
    """Request to create an ebarimt (electronic tax receipt)."""

    payment_id: str
    ebarimt_receiver_type: str
    ebarimt_receiver: str = ""
    district_code: str = ""
    classification_code: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "payment_id": self.payment_id,
            "ebarimt_receiver_type": self.ebarimt_receiver_type,
        }
        if self.ebarimt_receiver:
            d["ebarimt_receiver"] = self.ebarimt_receiver
        if self.district_code:
            d["district_code"] = self.district_code
        if self.classification_code:
            d["classification_code"] = self.classification_code
        return d


@dataclass
class EbarimtItem:
    """Item in an ebarimt response."""

    id: str = ""
    barimt_id: str = ""
    merchant_product_code: Optional[str] = None
    tax_product_code: str = ""
    bar_code: Optional[str] = None
    name: str = ""
    unit_price: str = ""
    quantity: str = ""
    amount: str = ""
    city_tax_amount: str = ""
    vat_amount: str = ""
    note: Optional[str] = None
    created_by: str = ""
    created_date: str = ""
    updated_by: str = ""
    updated_date: str = ""
    status: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EbarimtItem:
        return cls(
            id=data.get("id", ""),
            barimt_id=data.get("barimt_id", ""),
            merchant_product_code=data.get("merchant_product_code"),
            tax_product_code=data.get("tax_product_code", ""),
            bar_code=data.get("bar_code"),
            name=data.get("name", ""),
            unit_price=data.get("unit_price", ""),
            quantity=data.get("quantity", ""),
            amount=data.get("amount", ""),
            city_tax_amount=data.get("city_tax_amount", ""),
            vat_amount=data.get("vat_amount", ""),
            note=data.get("note"),
            created_by=data.get("created_by", ""),
            created_date=data.get("created_date", ""),
            updated_by=data.get("updated_by", ""),
            updated_date=data.get("updated_date", ""),
            status=data.get("status", False),
        )


@dataclass
class EbarimtHistory:
    """History entry in an ebarimt response."""

    id: str = ""
    barimt_id: str = ""
    ebarimt_receiver_type: str = ""
    ebarimt_receiver: str = ""
    ebarimt_register_no: Optional[str] = None
    ebarimt_bill_id: str = ""
    ebarimt_date: str = ""
    ebarimt_mac_address: str = ""
    ebarimt_internal_code: str = ""
    ebarimt_bill_type: str = ""
    ebarimt_qr_data: str = ""
    ebarimt_lottery: str = ""
    ebarimt_lottery_msg: Optional[str] = None
    ebarimt_error_code: Optional[str] = None
    ebarimt_error_msg: Optional[str] = None
    ebarimt_response_code: Optional[str] = None
    ebarimt_response_msg: Optional[str] = None
    note: Optional[str] = None
    barimt_status: str = ""
    barimt_status_date: str = ""
    ebarimt_sent_email: Optional[str] = None
    ebarimt_receiver_phone: str = ""
    tax_type: str = ""
    created_by: str = ""
    created_date: str = ""
    updated_by: str = ""
    updated_date: str = ""
    status: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EbarimtHistory:
        return cls(
            id=data.get("id", ""),
            barimt_id=data.get("barimt_id", ""),
            ebarimt_receiver_type=data.get("ebarimt_receiver_type", ""),
            ebarimt_receiver=data.get("ebarimt_receiver", ""),
            ebarimt_register_no=data.get("ebarimt_register_no"),
            ebarimt_bill_id=data.get("ebarimt_bill_id", ""),
            ebarimt_date=data.get("ebarimt_date", ""),
            ebarimt_mac_address=data.get("ebarimt_mac_address", ""),
            ebarimt_internal_code=data.get("ebarimt_internal_code", ""),
            ebarimt_bill_type=data.get("ebarimt_bill_type", ""),
            ebarimt_qr_data=data.get("ebarimt_qr_data", ""),
            ebarimt_lottery=data.get("ebarimt_lottery", ""),
            ebarimt_lottery_msg=data.get("ebarimt_lottery_msg"),
            ebarimt_error_code=data.get("ebarimt_error_code"),
            ebarimt_error_msg=data.get("ebarimt_error_msg"),
            ebarimt_response_code=data.get("ebarimt_response_code"),
            ebarimt_response_msg=data.get("ebarimt_response_msg"),
            note=data.get("note"),
            barimt_status=data.get("barimt_status", ""),
            barimt_status_date=data.get("barimt_status_date", ""),
            ebarimt_sent_email=data.get("ebarimt_sent_email"),
            ebarimt_receiver_phone=data.get("ebarimt_receiver_phone", ""),
            tax_type=data.get("tax_type", ""),
            created_by=data.get("created_by", ""),
            created_date=data.get("created_date", ""),
            updated_by=data.get("updated_by", ""),
            updated_date=data.get("updated_date", ""),
            status=data.get("status", False),
        )


@dataclass
class EbarimtResponse:
    """Response from creating or canceling an ebarimt."""

    id: str = ""
    ebarimt_by: str = ""
    g_wallet_id: str = ""
    g_wallet_customer_id: str = ""
    ebarimt_receiver_type: str = ""
    ebarimt_receiver: str = ""
    ebarimt_district_code: str = ""
    ebarimt_bill_type: str = ""
    g_merchant_id: str = ""
    merchant_branch_code: str = ""
    merchant_terminal_code: Optional[str] = None
    merchant_staff_code: Optional[str] = None
    merchant_register_no: str = ""
    g_payment_id: str = ""
    paid_by: str = ""
    object_type: str = ""
    object_id: str = ""
    amount: str = ""
    vat_amount: str = ""
    city_tax_amount: str = ""
    ebarimt_qr_data: str = ""
    ebarimt_lottery: str = ""
    note: Optional[str] = None
    barimt_status: str = ""
    barimt_status_date: str = ""
    ebarimt_sent_email: Optional[str] = None
    ebarimt_receiver_phone: str = ""
    tax_type: str = ""
    merchant_tin: str = ""
    ebarimt_receipt_id: str = ""
    created_by: str = ""
    created_date: str = ""
    updated_by: str = ""
    updated_date: str = ""
    status: bool = False
    barimt_items: list[EbarimtItem] = field(default_factory=list)
    barimt_transactions: list[Any] = field(default_factory=list)
    barimt_histories: list[EbarimtHistory] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EbarimtResponse:
        return cls(
            id=data.get("id", ""),
            ebarimt_by=data.get("ebarimt_by", ""),
            g_wallet_id=data.get("g_wallet_id", ""),
            g_wallet_customer_id=data.get("g_wallet_customer_id", ""),
            ebarimt_receiver_type=data.get("ebarimt_receiver_type", ""),
            ebarimt_receiver=data.get("ebarimt_receiver", ""),
            ebarimt_district_code=data.get("ebarimt_district_code", ""),
            ebarimt_bill_type=data.get("ebarimt_bill_type", ""),
            g_merchant_id=data.get("g_merchant_id", ""),
            merchant_branch_code=data.get("merchant_branch_code", ""),
            merchant_terminal_code=data.get("merchant_terminal_code"),
            merchant_staff_code=data.get("merchant_staff_code"),
            merchant_register_no=data.get("merchant_register_no", ""),
            g_payment_id=data.get("g_payment_id", ""),
            paid_by=data.get("paid_by", ""),
            object_type=data.get("object_type", ""),
            object_id=data.get("object_id", ""),
            amount=data.get("amount", ""),
            vat_amount=data.get("vat_amount", ""),
            city_tax_amount=data.get("city_tax_amount", ""),
            ebarimt_qr_data=data.get("ebarimt_qr_data", ""),
            ebarimt_lottery=data.get("ebarimt_lottery", ""),
            note=data.get("note"),
            barimt_status=data.get("barimt_status", ""),
            barimt_status_date=data.get("barimt_status_date", ""),
            ebarimt_sent_email=data.get("ebarimt_sent_email"),
            ebarimt_receiver_phone=data.get("ebarimt_receiver_phone", ""),
            tax_type=data.get("tax_type", ""),
            merchant_tin=data.get("merchant_tin", ""),
            ebarimt_receipt_id=data.get("ebarimt_receipt_id", ""),
            created_by=data.get("created_by", ""),
            created_date=data.get("created_date", ""),
            updated_by=data.get("updated_by", ""),
            updated_date=data.get("updated_date", ""),
            status=data.get("status", False),
            barimt_items=[
                EbarimtItem.from_dict(i) for i in data.get("barimt_items", [])
            ],
            barimt_transactions=data.get("barimt_transactions", []),
            barimt_histories=[
                EbarimtHistory.from_dict(h)
                for h in data.get("barimt_histories", [])
            ],
        )
