#!/usr/bin/env python3
import sys

def parse_cpu_line(line: str):
    parts = line.strip().split()
    if not parts or parts[0] != "CPU":
        return None

    try:
        hostname = parts[1]
        epoch    = int(parts[2])
        date     = parts[3]
        time     = parts[4]
        datetime = f"{date} {time}"
        interval = int(parts[5])
        load     = int(parts[6])
        ncpu     = int(parts[7])
    except (ValueError, IndexError):
        return None

    counters = []
    for p in parts[8:]:
        try:
            counters.append(int(p))
        except ValueError:
            continue

    fields = [
        "usr", "sys", "nice", "idle", "iowait",
        "irq", "softirq", "steal", "guest", "guest_nice"
    ]

    mapped = {}
    for i, name in enumerate(fields):
        if i < len(counters):
            mapped[name] = counters[i]

    extra = counters[len(fields):]

    return {
        "hostname": hostname,
        "epoch": epoch,
        "datetime": datetime,
        "interval": interval,
        "load": load,
        "ncpu": ncpu,
        "counters": mapped,
        "extra": extra,
    }


def compute_utilization(sample):
    counters = sample["counters"]
    total = sum(counters.values())
    if total <= 0:
        return {**{k: 0.0 for k in counters}, "total_util": 0.0}

    percentages = {k: (v / total) * 100 for k, v in counters.items()}
    idle = counters.get("idle", 0) + counters.get("iowait", 0)
    utilization = 100.0 * (total - idle) / total
    percentages["total_util"] = utilization
    return percentages


def main(filepath, average_mode=False):
    if filepath == "-":  # read from stdin
        lines = sys.stdin.readlines()
    else:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

    cpu_lines = [parse_cpu_line(line) for line in lines if line.startswith("CPU")]
    cpu_lines = [c for c in cpu_lines if c]  # drop None

    if not cpu_lines:
        print("No CPU samples found in input.")
        return

    if average_mode:
        total_util_sum = 0.0
        count = 0
        for sample in cpu_lines:
            util = compute_utilization(sample)
            total_util_sum += util["total_util"]
            count += 1
        avg_util = total_util_sum / count if count else 0.0
        print(f"Average CPU Utilization: {avg_util:.2f}% over {count} samples")
    else:
        for curr in cpu_lines:
            util = compute_utilization(curr)
            print(f"{curr['datetime']} | Host: {curr['hostname']} "
                  f"| CPU Utilization: {util['total_util']:.2f}% "
                  f"(usr={util.get('usr',0):.2f}%, sys={util.get('sys',0):.2f}%, "
                  f"iowait={util.get('iowait',0):.2f}%, idle={util.get('idle',0):.2f}%)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  atop -r /var/log/atop/atop_YYYYMMDD -P CPU | python code.py -")
        print("  python code.py atop_cpu.txt")
        print("  python code.py atop_cpu.txt --average")
        sys.exit(1)

    filepath = sys.argv[1]
    average_mode = len(sys.argv) > 2 and sys.argv[2] == "--average"
    main(filepath, average_mode)
