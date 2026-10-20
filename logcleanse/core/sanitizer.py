# logcleanse/core/sanitizer.py
import re
from typing import Tuple

class SecuritySanitizer:
    # Pre-compile regex at module import time to avoid runtime compilation overhead
    SQLI_PATTERN = re.compile(
        r"(\b(UNION(\s+ALL)?|SELECT|INSERT|DELETE|UPDATE|DROP)\b|--|\' OR \'1\'=\'1)", 
        re.IGNORECASE
    )
    XSS_PATTERN = re.compile(
        r"(<script.*?>.*?</script.*?>|javascript:|onload=|onerror=)", 
        re.IGNORECASE
    )
    BEARER_TOKEN_PATTERN = re.compile(
        r"(bearer\s+[a-zA-Z0-9_\-\.]{20,})", 
        re.IGNORECASE
    )

    @classmethod
    def sanitize_string(cls, raw_text: str) -> Tuple[str, bool]:
        """
        Scans and sanitizes strings.
        Returns:
            Tuple[sanitized_text, was_malicious]
        """
        is_threat = False
        text = raw_text

        if cls.SQLI_PATTERN.search(text) or cls.XSS_PATTERN.search(text):
            is_threat = True
            # Neutralize dangerous characters
            text = text.replace("'", "''").replace("<", "&lt;").replace(">", "&gt;")

        # Redact tokens regardless
        text = cls.BEARER_TOKEN_PATTERN.sub("[REDACTED_TOKEN]", text)
        return text, is_threat