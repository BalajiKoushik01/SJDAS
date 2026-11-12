"""
SJ-DAS Licensing Module.
Enterprise-Grade Security for Commercial Distribution.
"""

import hashlib
import hmac
import json
import logging
import os
import platform
import uuid
from datetime import datetime

logger = logging.getLogger("SJ_DAS.Licensing")


class LicenseManager:
    """
    Manages commercial licensing and anti-piracy checks.
    """

    def __init__(self):
        self.license_file = "license.key"
        self.machine_id = self._get_machine_id()
        self.status = "TRIAL"
        self.expiry = None

    def _get_machine_id(self):
        """Generate a unique fingerprint for this hardware."""
        info = [
            platform.node(),
            platform.processor(),
            str(uuid.getnode()),  # MAC Address
            platform.machine()
        ]
        unique_str = "_".join(info)
        return hashlib.sha256(unique_str.encode()).hexdigest()[:32].upper()

    def validate(self) -> bool:
        """Check machine binding and expiry; require a signature in production."""
        try:
            with open(self.license_file, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except FileNotFoundError:
            self.status = "TRIAL"
            return False
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            self.status = "INVALID"
            return False

        if not isinstance(data, dict) or data.get("machine_id") != self.machine_id:
            self.status = "INVALID"
            return False

        expiry_str = data.get("expiry")
        try:
            if expiry_str and datetime.now().date() > datetime.fromisoformat(expiry_str).date():
                self.status = "EXPIRED"
                return False
        except (TypeError, ValueError):
            self.status = "INVALID"
            return False

        if os.environ.get("APP_ENV", "development").lower() == "production":
            signing_key = os.environ.get("SJDAS_LICENSE_SIGNING_KEY")
            signature = data.get("signature")
            if not signing_key or not isinstance(signature, str):
                self.status = "INVALID"
                return False
            payload = f"{self.machine_id}:{expiry_str or ''}".encode("utf-8")
            expected = hmac.new(signing_key.encode("utf-8"), payload, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected):
                self.status = "INVALID"
                return False

        self.status = "PRO"
        self.expiry = expiry_str
        return True

    def generate_trial_license(self):
        """Create a default trial license."""
        data = {
            "machine_id": self.machine_id,
            "type": "TRIAL",
            "expiry": "2025-12-31"  # Default trial
        }
        # In production, this would be signed by server
        return data

    def get_status_message(self):
        if self.status == "PRO":
            return "Professional License (Active)"
        if self.status == "TRIAL":
            return f"Trial Mode - Machine ID: {self.machine_id}"
        return f"License Error: {self.status}"


# Global
_manager = None


def get_license_manager():
    global _manager
    if _manager is None:
        _manager = LicenseManager()
    return _manager
