#!/usr/bin/env bash
# A small package with a noisy, 300-test suite and two planted bugs.
set -euo pipefail
mkdir -p ledger tests
touch ledger/__init__.py tests/__init__.py
cat > ledger/money.py <<'PY'
def to_cents(amount):
    """Convert a dollar amount to integer cents."""
    return int(amount * 100)


def add(a, b):
    return round(a + b, 2)
PY
cat > ledger/paginate.py <<'PY'
def paginate(items, page, size):
    """Return page `page` (1-based) of `items`, `size` items per page."""
    start = (page - 1) * size
    end = page * size - 1
    return items[start:end]


def page_count(items, size):
    return (len(items) + size - 1) // size
PY
cat > ledger/dates.py <<'PY'
import datetime as _dt


def quarter(d):
    return (d.month - 1) // 3 + 1


def is_weekend(d):
    return d.weekday() >= 5


_ = _dt
PY
python3 - <<'PY'
lines = ["import unittest, datetime, logging, sys",
         "from ledger.money import to_cents, add",
         "from ledger.paginate import paginate, page_count",
         "from ledger.dates import quarter, is_weekend",
         "log = logging.getLogger('ledger')",
         "logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')",
         "", "class Generated(unittest.TestCase):"]
n = 0
for i in range(1, 99):
    n += 1
    lines += [f"    def test_add_{i}(self):",
              *[f"        log.debug('add case {i} step {k}: fixture loaded, ledger balanced, audit ok')" for k in range(8)],
              f"        self.assertEqual(add({i}, 0.5), {i + 0.5})"]
for i in range(1, 13):
    n += 1
    lines += [f"    def test_quarter_{i}(self):",
              *[f"        log.debug('quarter case {i} step {k}: calendar warmed, tz=UTC')" for k in range(8)],
              f"        self.assertEqual(quarter(datetime.date(2026, {i}, 1)), {(i - 1) // 3 + 1})"]
for i in range(1, 100):
    n += 1
    lines += [f"    def test_page_count_{i}(self):",
              *[f"        log.debug('page_count case {i} step {k}: list built')" for k in range(8)],
              f"        self.assertEqual(page_count(list(range({i})), 10), {(i + 9) // 10})"]
for i in range(1, 90):
    n += 1
    lines += [f"    def test_whole_dollars_{i}(self):",
              *[f"        log.debug('cents case {i} step {k}: currency USD')" for k in range(8)],
              f"        self.assertEqual(to_cents({i}), {i * 100})"]
lines += ["    def test_to_cents_rounding(self):",
          "        log.debug('rounding: 0.29 dollars')",
          "        self.assertEqual(to_cents(0.29), 29)",
          "    def test_paginate_first_page(self):",
          "        self.assertEqual(paginate(list(range(25)), 1, 10), list(range(10)))",
          "    def test_paginate_last_page(self):",
          "        self.assertEqual(paginate(list(range(25)), 3, 10), [20, 21, 22, 23, 24])",
          "", "if __name__ == '__main__':", "    unittest.main()"]
open("tests/test_ledger.py", "w").write("\n".join(lines) + "\n")
PY
