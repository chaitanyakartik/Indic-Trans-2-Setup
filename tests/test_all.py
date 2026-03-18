"""
Run all endpoint tests sequentially and report results.
Usage: python tests/test_all.py
"""
import subprocess
import sys
import time

TESTS = [
    ("Scanned PDF   (/translate-pdf)",   "tests/test_scanned_pdf.py"),
    ("Image         (/translate-image)", "tests/test_image.py"),
    ("Audio         (/translate-audio)", "tests/test_audio.py"),
]


def run(label, script):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    start = time.monotonic()
    result = subprocess.run([sys.executable, script], text=True)
    elapsed = time.monotonic() - start
    ok = result.returncode == 0
    print(f"\n[{'PASS' if ok else 'FAIL'}] {label}  ({elapsed:.1f}s)")
    return ok


def main():
    print("IndicTrans2 API — full test suite")
    print(f"Running {len(TESTS)} test(s)...\n")

    results = [(label, run(label, script)) for label, script in TESTS]

    print(f"\n{'='*60}")
    print("  SUMMARY")
    print(f"{'='*60}")
    all_passed = True
    for label, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}]  {label}")
        if not ok:
            all_passed = False

    print()
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
