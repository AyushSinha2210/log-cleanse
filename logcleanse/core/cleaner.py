# logcleanse/core/cleaner.py
import csv
from typing import Iterator, Dict, Any, Tuple, List
from logcleanse.core.stats import RunningStats
from logcleanse.core.sanitizer import SecuritySanitizer
from logcleanse.core.schema import FieldValidator, is_valid_ipv4

class LogStreamCleaner:
    def __init__(self, drop_invalid: bool = True) -> None:
        self.drop_invalid = drop_invalid
        self.response_time_stats = RunningStats()
        self.total_rows_read: int = 0
        self.dropped_rows_count: int = 0
        self.security_threats_neutralized: int = 0

        # Define dataset schema
        self.validators: Dict[str, FieldValidator] = {
            "timestamp": FieldValidator("timestamp", str, required=True),
            "user_id": FieldValidator("user_id", int, required=True, min_value=1),
            "ip_address": FieldValidator("ip_address", str, required=True, custom_check=is_valid_ipv4),
            "request_path": FieldValidator("request_path", str, required=True),
            "response_time_ms": FieldValidator("response_time_ms", float, required=True, min_value=0.0, max_value=60000.0),
            "status_code": FieldValidator("status_code", int, required=True, min_value=100, max_value=599)
        }

    def process_stream(self, file_iterator: Iterator[str]) -> Iterator[Tuple[str, ...]]:
        reader = csv.reader(file_iterator)
        
        # Read and validate header
        header = next(reader, None)
        if not header:
            return
        
        header_map = {col.strip(): idx for idx, col in enumerate(header)}
        yield tuple(header)  # Yield clean header back

        for raw_row in reader:
            self.total_rows_read += 1
            if len(raw_row) != len(header):
                self.dropped_rows_count += 1
                continue

            cleaned_row: List[str] = list(raw_row)
            row_is_valid = True

            # 1. Schema Validation & Type Casting
            for field_name, validator in self.validators.items():
                col_idx = header_map.get(field_name)
                if col_idx is None:
                    continue
                try:
                    casted_val = validator.validate(raw_row[col_idx])
                    cleaned_row[col_idx] = str(casted_val)
                except ValueError:
                    row_is_valid = False
                    break

            if not row_is_valid:
                self.dropped_rows_count += 1
                if self.drop_invalid:
                    continue

            # 2. Security Sanitization on text columns
            path_idx = header_map["request_path"]
            clean_path, was_threat = SecuritySanitizer.sanitize_string(cleaned_row[path_idx])
            cleaned_row[path_idx] = clean_path
            if was_threat:
                self.security_threats_neutralized += 1

            # 3. Stream Welford Statistics on response_time_ms
            time_idx = header_map["response_time_ms"]
            self.response_time_stats.update(float(cleaned_row[time_idx]))

            yield tuple(cleaned_row)