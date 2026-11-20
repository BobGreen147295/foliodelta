"""Local evidence for a same-store order export discrepancy. Python 3.10+."""
import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


NORMAL = ("order_id", "created_at", "total", "currency")
SHOPIFY = ("Name", "Created at", "Total", "Currency")
# Supported settlement currencies and their minor-unit precision.
PRECISION = {"USD": 2, "EUR": 2, "GBP": 2, "CAD": 2, "AUD": 2, "NZD": 2,
             "CHF": 2, "SGD": 2, "HKD": 2, "CNY": 2, "JPY": 0, "KWD": 3}


class InputIssue(ValueError):
    pass


def read_orders(path, side):
    row = 1

    def fail(message):
        raise InputIssue(f"{side}, line {row}: {message}")

    orders = {}
    previous = None
    currency = None
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.reader(stream, strict=True)
            header = next(reader, [])
            if len(header) != len(set(header)):
                fail("duplicate headers")
            schemas = [s for s in (NORMAL, SHOPIFY) if set(s) <= set(header)]
            if len(schemas) != 1:
                fail("expected Shopify order headers or order_id,created_at,total,currency")
            schema = schemas[0]
            indexes = [header.index(k) for k in schema]
            item_index = header.index("Lineitem name") if schema == SHOPIFY and "Lineitem name" in header else None
            while True:
                row = reader.line_num + 1
                cells = next(reader, None)
                if cells is None:
                    break
                if not cells:
                    continue
                if len(cells) != len(header):
                    fail("column count differs from header")
                key, stamp, amount, unit = [cells[i].strip() for i in indexes]
                if not key or len(key) > 160 or not key.isprintable():
                    fail("invalid order identifier")
                if item_index is not None and cells[item_index].strip() and key == previous and not any((stamp, amount, unit)):
                    continue
                if key in orders:
                    fail("repeated order summary or ambiguous item row; check the original export")
                if unit not in PRECISION or (currency and unit != currency):
                    fail("unsupported or mixed currency")
                if not re.fullmatch(r"-?[0-9]{1,15}(?:\.[0-9]{1,6})?", amount):
                    fail("invalid decimal total")
                whole, _, fraction = amount.lstrip("-").partition(".")
                scale = PRECISION[unit]
                if fraction[scale:].strip("0"):
                    fail("amount exceeds currency precision")
                minor = int(whole + fraction[:scale].ljust(scale, "0"))
                try:
                    iso = re.sub(r" ?([+-][0-9]{2}):?([0-9]{2})$", r"\1:\2", stamp.replace("Z", "+00:00"))
                    moment = datetime.fromisoformat(iso)
                    if moment.utcoffset() is None:
                        raise ValueError()
                    utc = moment.astimezone(timezone.utc).isoformat()
                except (ValueError, OverflowError):
                    fail("creation timestamp requires a valid UTC offset")
                orders[key] = (row, -minor if amount.startswith("-") else minor, utc)
                previous, currency = key, unit
    except (UnicodeError, csv.Error):
        fail("invalid UTF-8 or CSV encoding/quoting")
    except OSError:
        fail("cannot read file")
    return orders, currency


def compare(left_path, right_path, confirmed=False):
    left, lu = read_orders(left_path, "left")
    right, ru = read_orders(right_path, "right")
    if lu and ru and lu != ru:
        raise InputIssue("currency differs between exports; compare one currency at a time")
    if not (lu or ru):
        raise InputIssue("both exports are empty; currency unknown")
    changes = []
    for key in left.keys() | right.keys():
        a, b = left.get(key), right.get(key)
        if a and b and a[1:] == b[1:]:
            continue
        delta = (b[1] if b else 0) - (a[1] if a else 0)
        def evidence(record):
            return dict(line=record[0], minor=record[1], utc=record[2]) if record else None
        changes.append(dict(order=key, kind="changed" if a and b else "left_only" if a else "right_only",
                            left=evidence(a), right=evidence(b), delta_minor=delta))
    changes.sort(key=lambda change: (-abs(change["delta_minor"]), change["order"]))
    left_total = sum(record[1] for record in left.values())
    right_total = sum(record[1] for record in right.values())
    return dict(schema="foliodelta/1", scope="operator_declared" if confirmed else "unconfirmed",
                currency=lu or ru, precision=PRECISION[lu or ru], left_count=len(left), right_count=len(right),
                left_minor=left_total, right_minor=right_total, delta_minor=right_total-left_total,
                changes=changes, next_check="Verify export filters, window, status and total definition; trace the listed orders in the source.",
                limit="File differences alone cannot establish missing sales, refunds, profit or cause.")


def handoff(report):
    def money(minor):
        scale = report["precision"]
        whole, fraction = divmod(abs(minor), 10**scale)
        decimal = f".{fraction:0{scale}d}" if scale else ""
        return f"{'-' if minor < 0 else ''}{whole}{decimal} {report['currency']}"

    if report.get("sample") == "bundled_fictional":
        print("Fictional demo orders")
    print("Order reconciliation | scope:", report["scope"])
    print(f"Left ({report['left_count']} orders): {money(report['left_minor'])}")
    print(f"Right ({report['right_count']} orders): {money(report['right_minor'])}")
    print("Right minus left:", money(report["delta_minor"]))
    print("Changed or one-sided orders:", len(report["changes"]))
    shown = report["changes"][:10]
    if len(shown) < len(report["changes"]):
        print("Showing the top 10 by absolute delta. Use --json for all rows.")
    for change in shown:
        details = []
        for side in ("left", "right"):
            source = change[side]
            details.append(f"{side} line {source['line']}, {money(source['minor'])}, {source['utc']}" if source else f"{side} absent")
        print(f"{change['order']} | {change['kind']} | {money(change['delta_minor'])} | " + " | ".join(details))
    if any(c["kind"] != "changed" for c in shown):
        print("One-sided orders: search the order in the source store and compare export filters before calling it missing.")
    if any(c["kind"] == "changed" and c["delta_minor"] for c in shown):
        print("Amount changes: inspect the order history and refund transactions before assigning a cause.")
    print(report["next_check"])
    print(report["limit"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--scope-confirmed", action="store_true", help="operator confirmed same store, window, filters and amount definition")
    parser.add_argument("--json", action="store_true", help="write machine-readable evidence to stdout")
    args = parser.parse_args()
    try:
        result = compare(args.left, args.right, args.scope_confirmed)
    except InputIssue as exc:
        parser.exit(2, str(exc) + "\n")
    examples = Path(__file__).resolve().parents[1] / "examples"
    if {args.left.resolve(), args.right.resolve()} == {examples / "before.csv", examples / "after.csv"}:
        result["sample"] = "bundled_fictional"
    if args.json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        handoff(result)


if __name__ == "__main__":
    sys.exit(main())
