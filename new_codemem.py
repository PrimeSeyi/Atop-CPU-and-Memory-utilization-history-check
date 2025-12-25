#!/usr/bin/env python3
import sys
import argparse
from typing import List, Optional

def split_mem_lines(lines: List[str]) -> List[List[str]]:
    out = []
    for l in lines:
        if not l.strip():
            continue
        if l.startswith("MEM "):
            parts = l.split()
            out.append(parts[2:])  # drop "MEM" and hostname
    return out

def detect_pagesize_index(parts_list: List[List[str]]) -> Optional[int]:
    for idx in range(0, min(10, min(len(p) for p in parts_list))):
        try:
            vals = [int(p[idx]) for p in parts_list]
        except ValueError:
            continue
        if all(v in (4096, 8192) for v in vals):
            return idx
    return None

def parse_and_compute(parts_list: List[List[str]], pagesize_idx: int, avail_idx: int):
    total_idx = pagesize_idx + 1
    records = []
    for parts in parts_list:
        try:
            pagesize_bytes = int(parts[pagesize_idx])
            total_pages = int(parts[total_idx])
            avail_pages = int(parts[avail_idx])
        except Exception as e:
            print(f"⚠️ Skipping line: {e}")
            print("LINE:", parts)
            continue

        page_kb = pagesize_bytes // 1024
        total_kb = total_pages * page_kb
        avail_kb = avail_pages * page_kb
        used_kb = total_kb - avail_kb
        used_pct = (used_kb / total_kb * 100.0) if total_kb > 0 else 0.0
        ts = parts[1] + " " + parts[2]
        records.append({
            "ts": ts,
            "total_kb": total_kb,
            "avail_kb": avail_kb,
            "used_kb": used_kb,
            "used_pct": used_pct,
            "avail_idx": avail_idx,
        })
    return records

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", default="-")
    parser.add_argument("--average", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    lines = sys.stdin.readlines() if args.file == "-" else open(args.file).readlines()

    parts_list = split_mem_lines(lines)
    if not parts_list:
        print("No MEM lines found.")
        return

    pagesize_idx = detect_pagesize_index(parts_list) or 4
    avail_idx = 28  # FIXED: Available pages index

    if args.debug:
        print(f"Using pagesize_idx={pagesize_idx}, avail_idx={avail_idx}")

    records = parse_and_compute(parts_list, pagesize_idx, avail_idx)

    if not records:
        print("⚠️ No valid records parsed.")
        return

    if not args.average:
        for r in records:
            print(f"{r['ts']} | Used: {r['used_kb']:,} kB ({r['used_pct']:.2f}%) | "
                  f"Total: {r['total_kb']:,} kB | Available(idx{r['avail_idx']})={r['avail_kb']:,} kB")

    avg_used_kb = sum(r['used_kb'] for r in records) / len(records)
    avg_total_kb = sum(r['total_kb'] for r in records) / len(records)
    avg_pct = (avg_used_kb / avg_total_kb * 100.0) if avg_total_kb > 0 else 0.0
    print(f"\nAverage Memory Utilization: {avg_pct:.2f}% ({avg_used_kb:,.0f} kB avg used) over {len(records)} samples")

if __name__ == "__main__":
    main()
