
# Atop Memory Log Parser & Analyzer

## Overview

This tool is a Python script designed to parse the machine-readable output (`-P MEM`) from `atop` logs. It calculates real-time memory usage and utilization percentages, allowing you to identify memory leaks or exhaustion events historically.

It is specifically designed to be **cross-compatible** with both modern Linux distributions (running `atop` v2.x+) and legacy systems (running older versions).

---

## How It Works

The script reads the raw, pipe-delimited output from `atop` and performs the following operations:

### 1. Auto-Detection

It scans the input lines to determine which version of `atop` generated the log.

* **Modern Mode**
  If it detects extended columns (29+ fields), it uses the explicit **Available Memory** counter provided by the kernel.

* **Legacy Mode**
  If it detects the shorter format common on older OS versions (Ubuntu 18.04, CentOS 7), it automatically switches to a fallback calculation method.

---

### 2. The Math

* **Total Memory**
  Read directly from the log.

* **Available Memory**

  * **Modern:** Uses the pre-calculated kernel value.
  * **Legacy:** Calculates `Free + Cache + Buffer` to estimate available resources.

* **Used Memory**
  `Total - Available`

* **Utilization %**
  `(Used / Total) * 100`

---

## Usage

You can pipe `atop` output directly into the script, or run it against a saved text file.

### 1. Analyze a Specific Log File (Live Pipe)

This is the most common method. It reads the binary log for a specific date (e.g., Dec 16, 2025) and parses the memory lines.

```bash
atop -r /var/log/atop/atop_20251216 -P MEM | python3 codemem.py -
```

---

### 2. Analyze a Saved Text File

If you have already saved the output to a file:

```bash
python3 codemem.py memory_dump.txt
```

---

### 3. Calculate Daily Average

To get a quick summary of the average memory consumption for the entire duration of the log:

```bash
atop -r /var/log/atop/atop_20251216 -P MEM | python3 codemem.py - --average
```

---

## The Code (`codemem.py`)

I saved the  code into a file named `codemem.py`. It requires **Python 3.6 or higher** and has **no external dependencies** (no `pip install` required).




---

# Atop CPU Log Parser & Analyzer

## Overview

This tool parses the machine-readable output (`-P CPU`) from `atop` logs to calculate CPU utilization percentages. It breaks down usage into specific categories (User, System, Nice, IOWait) and provides a clear, time-stamped summary of server load.

It is designed to be **universal**, working seamlessly on both legacy systems (older Linux kernels) and modern systems without modification.

---

## How It Works

### 1. Universal Parsing

* Standard CPU counters (`User`, `Nice`, `System`, `Idle`) always appear at the *start* of the data line in `atop`.
* Newer counters (`Steal`, `Guest`) appear at the *end*.
* The script reads columns from left to right. On older machines where extra columns are missing, it stops reading to prevent "Index Out of Range" errors.

### 2. Order Correction

* `atop` raw output uses a specific order: `User`, `Nice`, `System`, `Idle`.
* The script strictly maps these indices to ensure "Nice" processes (background tasks) are not mistaken for "System" (kernel) load.

### 3. Calculation Logic

* Sums all counters to determine total CPU ticks for the interval.
* **Active Utilization**: `100% - (Idle % + IOWait %)`
* Reports **IOWait** explicitly to help identify performance issues caused by slow disks rather than slow code.

---

## Usage

You can pipe `atop` output directly into the script or run it against a saved text file.

### 1. Analyze a Specific Log File (Live Pipe)

```bash
atop -r /var/log/atop/atop_20251216 -P CPU | python3 codecpu.py -
```

---

### 2. Analyze a Saved Text File

```bash
python3 codecpu.py cpu_dump.txt
```

---

### 3. Calculate Daily Average

```bash
atop -r /var/log/atop/atop_20251216 -P CPU | python3 codecpu.py - --average
```

---

## The Code (`codecpu.py`)

Save the following code into a file named `codecpu.py`.

It requires **Python 3.6 or higher** and has **no external dependencies**.



---
]
