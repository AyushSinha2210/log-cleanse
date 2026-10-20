# LogCleanse

LogCleanse is a standard-library-only Python utility for cleaning, validating,
and sanitizing authentication log data without loading the complete dataset
into memory.

The streaming pipeline:

- Reads CSV rows incrementally.
- Validates and type-casts the supported schema.
- Drops invalid rows by default.
- Neutralizes SQL- and HTML-like payloads in request paths.
- Calculates response-time statistics using Welford's online algorithm.
- Writes cleaned data and an audit report.

## Requirements

- Python 3.9 or newer.
- No external third-party packages are required. All application and test
  functionality uses the Python standard library.

## Input schema

The input CSV must contain these columns:

```text
timestamp,user_id,ip_address,request_path,response_time_ms,status_code
```

## Generate sample data

From the project directory, generate a 10,000-row dirty sample:

```powershell
python dirty_data_generator.py
```

This creates `dirty_auth_logs.csv`.

## Run the CLI

Run the cleaner from the project directory:

```powershell
python -m logcleanse.cli `
    --input dirty_auth_logs.csv `
    --output clean_output.csv `
    --report report.json
```

The same command on one line is:

```powershell
python -m logcleanse.cli --input dirty_auth_logs.csv --output clean_output.csv --report report.json
```

The CLI writes:

- `clean_output.csv`: validated and sanitized rows.
- `report.json`: row counts, neutralized security threats, and response-time
  statistics.

Invalid rows are dropped by default. To retain invalid rows using the
cleaner's imputation behavior, add `--keep-invalid`:

```powershell
python -m logcleanse.cli `
    --input dirty_auth_logs.csv `
    --output clean_output.csv `
    --report report.json `
    --keep-invalid
```

On Windows, use `python` or `py` rather than `python3`. PowerShell uses a
backtick (`` ` ``) for line continuation; a backslash is not a continuation
character.

## Run the tests

The tests use Python's built-in `unittest` framework:

```powershell
python -m unittest discover -s tests -v
```

Verified output:

```text
Ran 2 tests in 0.000s

OK
```

## Memory benchmark

Run the `tracemalloc` benchmark:

```powershell
python benchmark_memory.py
```

The benchmark compares loading every row into a list of dictionaries with the
streaming `LogStreamCleaner` pipeline. The following is the actual output
captured from this project:

```text
[*] Preparing 100,000 rows for memory profiling...
[+] Generated 100000 dirty log rows in 'benchmark_100k.csv'.
[*] Raw dataset size on disk: 6.10 MiB

-----------------------------------------------------------------
Strategy                  | Peak RAM        | Runtime (s)
-----------------------------------------------------------------
Naive (Full In-Memory)    | 66.94 MiB       | 1.80
Streaming (logcleanse)    | 319.82 KiB      | 8.00
-----------------------------------------------------------------

[+] Memory Reduction: 99.53% lower peak RAM.
[+] Memory Invariant: Streaming peak is bounded by buffer size, not dataset size.
```

The streaming implementation processes one CSV row at a time and maintains
only running counters and statistics. Its working memory is therefore bounded
by the row/buffer size rather than the number of rows: **O(1) auxiliary memory
with respect to dataset size**. The naive comparison intentionally has
**O(N)** memory usage.

The benchmark removes its temporary `benchmark_100k.csv` and
`benchmark_sink.csv` files when it finishes.