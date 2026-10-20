# logcleanse/core/schema.py
from dataclasses import dataclass
from typing import Any, Callable, Optional
import ipaddress

@dataclass(frozen=True)
class FieldValidator:
    name: str
    target_type: type
    required: bool = True
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    custom_check: Optional[Callable[[Any], bool]] = None

    def validate(self, raw_value: str) -> Any:
        stripped = raw_value.strip()
        if not stripped:
            if self.required:
                raise ValueError(f"Field '{self.name}' is required but empty.")
            return None

        # Type conversion
        try:
            val = self.target_type(stripped)
        except (ValueError, TypeError):
            raise ValueError(f"Field '{self.name}' failed conversion to {self.target_type.__name__}.")

        # Boundary checks
        if self.min_value is not None and val < self.min_value:
            raise ValueError(f"Field '{self.name}' value {val} is below minimum {self.min_value}.")
        if self.max_value is not None and val > self.max_value:
            raise ValueError(f"Field '{self.name}' value {val} exceeds maximum {self.max_value}.")

        # Custom lambda checks (e.g., IPv4 parsing)
        if self.custom_check and not self.custom_check(val):
            raise ValueError(f"Field '{self.name}' failed custom validation.")

        return val


def is_valid_ipv4(ip_str: str) -> bool:
    try:
        ipaddress.IPv4Address(ip_str)
        return True
    except ipaddress.AddressValueError:
        return False