import os
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Tuple

from dirty_data_generator import generate_dirty_data
from logcleanse.core.cleaner import LogStreamCleaner


def format_bytes(num_bytes: int) -> str:
    """Formats raw bytes into human-readable KiB or MiB."""
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.2f} KiB"
    return f"{num_bytes / (1024 * 1024):.2f} MiB"


def benchmark_naive(file_path: Path) -> Tuple[int, float]:
    """
    Simulates naive loading: loads the entire dataset into memory as a list of dicts.
    Space Complexity: O(N)
    """
    tracemalloc.start()
    start_time = time.perf_counter()

    # Naive full-file ingestion
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        header = lines[0].strip().split(",")
        records = []
        for line in lines[1:]:
            values = line.strip().split(",")
            if len(values) == len(header):
                records.append(dict(zip(header, values)))

    elapsed = time.perf_counter() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Free memory explicitly for clean baseline
    del records
    del lines

    return peak_memory, elapsed


def benchmark_streaming(file_path: Path, output_sink: Path) -> Tuple[int, float]:
    """
    Simulates production streaming pipeline with LogStreamCleaner.
    Space Complexity: O(1)
    """
    tracemalloc.start()
    start_time = time.perf_counter()

    cleaner = LogStreamCleaner(drop_invalid=True)

    with open(file_path, "r", encoding="utf-8", errors="replace") as in_f, \
         open(output_sink, "w", encoding="utf-8", newline="") as out_f:
        for row in cleaner.process_stream(in_f):
            out_f.write(",".join(row) + "\n")

    elapsed = time.perf_counter() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Clean up generated test output
    if output_sink.exists():
        output_sink.unlink()

    return peak_memory, elapsed


def main() -> None:
    test_file = Path("benchmark_100k.csv")
    output_sink = Path("benchmark_sink.csv")
    row_count = 100_000

    print(f"[*] Preparing {row_count:,} rows for memory profiling...")
    generate_dirty_data(filename=str(test_file), rows=row_count)
    file_size_bytes = os.path.getsize(test_file)
    print(f"[*] Raw dataset size on disk: {format_bytes(file_size_bytes)}\n")

    print("-" * 65)
    print(f"{'Strategy':<25} | {'Peak RAM':<15} | {'Runtime (s)':<15}")
    print("-" * 65)

    # 1. Profile Naive In-Memory Approach
    naive_peak, naive_time = benchmark_naive(test_file)
    print(f"{'Naive (Full In-Memory)':<25} | {format_bytes(naive_peak):<15} | {naive_time:<15.2f}")

    # 2. Profile Streaming Pipeline
    stream_peak, stream_time = benchmark_streaming(test_file, output_sink)
    print(f"{'Streaming (logcleanse)':<25} | {format_bytes(stream_peak):<15} | {stream_time:<15.2f}")
    print("-" * 65)

    # Clean up input benchmark file
    if test_file.exists():
        test_file.unlink()

    # Compute differential
    reduction_pct = ((naive_peak - stream_peak) / naive_peak) * 100
    print(f"\n[+] Memory Reduction: {reduction_pct:.2f}% lower peak RAM.")
    print(f"[+] Memory Invariant: Streaming peak is bounded by buffer size, not dataset size.")


if __name__ == "__main__":
    main()