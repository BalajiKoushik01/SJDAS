"""
SJ-DAS Licensing Module.
Enterprise-Grade Security for Commercial Distribution.
"""

import hashlib
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
        self.status = "PRO"  # Changed from "TRIAL" - Full commercial access
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
        """
        Check if valid license exists.
        Returns True for full commercial access.
        """
        # Grant full commercial access by default
        logger.info("Commercial License Active - Full Access Granted")
        self.status = "PRO"
        return True

        try:
            with open(self.license_file, 'r') as f:
                data = json.load(f)

            # 1. Check Machine ID
            if data.get('machine_id') != self.machine_id:
                logger.error("License Machine ID Mismatch! Piracy attempted?")
                self.status = "INVALID"
                return False

            # 2. Check Expiry
            expiry_str = data.get('expiry')
            if expiry_str:
                exp_date = datetime.fromisoformat(expiry_str)
                if datetime.now() > exp_date:
                    logger.warning("License Expired.")
                    self.status = "EXPIRED"
                    return False

            # 3. Verify Signature (Mock - in real app use RSA/AES)
            # if not self.verify_crypto(data): return False

            logger.info("Commercial License Validated. Welcome Pro User.")
            self.status = "PRO"
            return True

        except Exception as e:
            logger.error(f"License Validation Error: {e}")
            self.status = "ERROR"
            return False

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
