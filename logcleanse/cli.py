# logcleanse/cli.py
import argparse
import json
import sys
from pathlib import Path
from logcleanse.core.cleaner import LogStreamCleaner

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="logcleanse",
        description="Stream-clean, sanitize, and validate datasets with constant memory."
    )
    parser.add_argument("--input", "-i", type=Path, required=True, help="Path to input dirty CSV")
    parser.add_argument("--output", "-o", type=Path, required=True, help="Path to output clean CSV")
    parser.add_argument("--report", "-r", type=Path, required=True, help="Path to output JSON audit metrics")
    parser.add_argument("--keep-invalid", action="store_true", help="Impute instead of dropping invalid rows")

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)

    cleaner = LogStreamCleaner(drop_invalid=not args.keep_invalid)

    # Streaming I/O with constant memory allocation
    with open(args.input, mode="r", encoding="utf-8", errors="replace") as in_f, \
         open(args.output, mode="w", encoding="utf-8", newline="") as out_f:
        
        # Iterate over output rows and write directly
        for row in cleaner.process_stream(in_f):
            out_f.write(",".join(row) + "\n")

    # Generate Audit Metrics
    report_data = {
        "total_rows_read": cleaner.total_rows_read,
        "dropped_rows": cleaner.dropped_rows_count,
        "valid_rows_retained": cleaner.total_rows_read - cleaner.dropped_rows_count,
        "security_threats_neutralized": cleaner.security_threats_neutralized,
        "response_time_metrics": {
            "count": cleaner.response_time_stats.count,
            "mean_ms": round(cleaner.response_time_stats.mean, 4),
            "sample_variance": round(cleaner.response_time_stats.sample_variance, 4),
            "std_dev_ms": round(cleaner.response_time_stats.std_dev, 4)
        }
    }

    with open(args.report, "w", encoding="utf-8") as rep_f:
        json.dump(report_data, rep_f, indent=2)

    print(f"[+] Processing Complete.")
    print(f"    - Cleaned data written to: {args.output}")
    print(f"    - Metrics written to:      {args.report}")

if __name__ == "__main__":
    main()