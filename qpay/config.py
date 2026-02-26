"""QPay configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class QPayConfig:
    """Configuration for the QPay client."""

    base_url: str
    username: str
    password: str
    invoice_code: str
    callback_url: str

    @classmethod
    def from_env(cls) -> QPayConfig:
        """Load configuration from environment variables.

        Required environment variables:
            QPAY_BASE_URL: QPay API base URL
            QPAY_USERNAME: QPay merchant username
            QPAY_PASSWORD: QPay merchant password
            QPAY_INVOICE_CODE: Default invoice code
            QPAY_CALLBACK_URL: Payment callback URL

        Raises:
            ValueError: If any required environment variable is not set.
        """
        env_map = {
            "QPAY_BASE_URL": "base_url",
            "QPAY_USERNAME": "username",
            "QPAY_PASSWORD": "password",
            "QPAY_INVOICE_CODE": "invoice_code",
            "QPAY_CALLBACK_URL": "callback_url",
        }

        values: dict[str, str] = {}
        missing: list[str] = []

        for env_name, field_name in env_map.items():
            val = os.environ.get(env_name, "")
            if not val:
                missing.append(env_name)
            values[field_name] = val

        if missing:
            raise ValueError(
                f"Required environment variable(s) not set: {', '.join(missing)}"
            )

        return cls(**values)
