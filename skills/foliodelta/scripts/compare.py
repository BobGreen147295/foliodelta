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


REVIEW_STEPS = {
    "left_only": ("Order operations", "Find the order in the source store and check the right export's filters and cutoff."),
    "right_only": ("Order operations", "Find the order in the source store and check the left export's filters and cutoff."),
    "amount_changed": ("Payments or order operations", "Compare the order edit history and successful refund transactions by order, amount and currency."),
    "time_only": ("Reporting operations", "Compare the source creation timestamp, timezone and reporting cutoff."),
}


def minor_units(value, unit, location, field):
    if not re.fullmatch(r"-?[0-9]{1,15}(?:\.[0-9]{1,6})?", value):
        raise InputIssue(f"{location}: invalid decimal {field}")
    whole, _, fraction = value.lstrip("-").partition(".")
    scale = PRECISION[unit]
    if fraction[scale:].strip("0"):
        raise InputIssue(f"{location}: {field} exceeds currency precision")
    minor = int(whole + fraction[:scale].ljust(scale, "0"))
    return -minor if value.startswith("-") else minor


def read_orders(path, side, review_refunds=False):
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
            refund_index = None
            if review_refunds:
                if schema != SHOPIFY or "Refunded Amount" not in header:
                    fail("refund review requires a native Shopify order CSV with Refunded Amount")
                refund_index = header.index("Refunded Amount")
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
                refund = cells[refund_index].strip() if refund_index is not None else ""
                if not key or len(key) > 160 or not key.isprintable():
                    fail("invalid order identifier")
                if item_index is not None and cells[item_index].strip() and key == previous and not any((stamp, amount, unit)):
                    if refund:
                        fail("refund amount on an item continuation; verify the order summary")
                    continue
                if key in orders:
                    fail("repeated order summary or ambiguous item row; check the original export")
                if unit not in PRECISION or (currency and unit != currency):
                    fail("unsupported or mixed currency")
                location = f"{side}, line {row}"
                minor = minor_units(amount, unit, location, "total")
                refund_minor = minor_units(refund, unit, location, "refunded amount") if refund else None
                try:
                    iso = re.sub(r" ?([+-][0-9]{2}):?([0-9]{2})$", r"\1:\2", stamp.replace("Z", "+00:00"))
                    moment = datetime.fromisoformat(iso)
                    if moment.utcoffset() is None:
                        raise ValueError()
                    utc = moment.astimezone(timezone.utc).isoformat()
                except (ValueError, OverflowError):
                    fail("creation timestamp requires a valid UTC offset")
                orders[key] = (row, minor, utc, refund_minor)
                previous, currency = key, unit
    except (UnicodeError, csv.Error):
        fail("invalid UTF-8 or CSV encoding/quoting")
    except OSError:
        fail("cannot read file")
    return orders, currency


def refund_review(left, right):
    changes, blanks = [], []
    matched = left.keys() & right.keys()
    for key in sorted(matched):
        a, b = left[key], right[key]
        before, after = a[3], b[3]
        entry = dict(order=key, left_line=a[0], right_line=b[0], left_minor=before, right_minor=after)
        if before is None or after is None:
            blanks.append(entry)
        elif before != after:
            changes.append(dict(**entry, delta_minor=after-before))
    changes.sort(key=lambda item: -abs(item["delta_minor"]))
    comparable = len(matched) - len(blanks)
    return dict(comparable=comparable, one_sided=len(left)+len(right)-2*len(matched),
                missing_values=blanks, changes=changes,
                comparable_delta_minor=sum(item["delta_minor"] for item in changes) if comparable else None,
                limit="Recorded amounts on comparable orders only. Confirm transfer status and date with payment transactions.")


def first_order_check(left, right, shared, changes):
    if not left or not right:
        empty_side = "left" if not left else "right"
        return f"The {empty_side} export has no order rows. Check its window and status filters in the store."
    if not shared:
        return ("No order keys match. Verify the store, export windows and identifier format "
                "on both files before investigating individual orders.")
    if not changes:
        return "The compared order keys, totals and creation times agree. Verify export coverage before closing the review."
    first = changes[0]
    lines = " and ".join(f"{side} line {first[side]['line']}" for side in ("left", "right") if first[side])
    category = first["kind"]
    if category == "changed":
        category = "amount_changed" if first["delta_minor"] else "time_only"
    return f"Start with {first['order']} ({lines}). {REVIEW_STEPS[category][1]}"


def compare(left_path, right_path, confirmed=False, review_refunds=False):
    left, lu = read_orders(left_path, "left", review_refunds)
    right, ru = read_orders(right_path, "right", review_refunds)
    if lu and ru and lu != ru:
        raise InputIssue("currency differs between exports; compare one currency at a time")
    if not (lu or ru):
        raise InputIssue("both exports are empty; currency unknown")
    changes = []
    for key in left.keys() | right.keys():
        a, b = left.get(key), right.get(key)
        if a and b and a[1:3] == b[1:3]:
            continue
        delta = (b[1] if b else 0) - (a[1] if a else 0)
        def evidence(record):
            return dict(line=record[0], minor=record[1], utc=record[2]) if record else None
        changes.append(dict(order=key, kind="changed" if a and b else "left_only" if a else "right_only",
                            left=evidence(a), right=evidence(b), delta_minor=delta))
    changes.sort(key=lambda change: (-abs(change["delta_minor"]), change["order"]))
    groups = {}
    for change in changes:
        category = change["kind"]
        delta = change["delta_minor"]
        if category == "changed":
            category = "amount_changed" if delta else "time_only"
        role, check = REVIEW_STEPS[category]
        group = groups.setdefault(category, dict(count=0, increase_minor=0, decrease_minor=0,
                                                  suggested_role=role, next_check=check))
        group["count"] += 1
        group["increase_minor"] += max(0, delta)
        group["decrease_minor"] += min(0, delta)
    left_total = sum(record[1] for record in left.values())
    right_total = sum(record[1] for record in right.values())
    shared = len(left.keys() & right.keys())
    report = dict(schema="foliodelta/1", scope="operator_declared" if confirmed else "unconfirmed",
                currency=lu or ru, precision=PRECISION[lu or ru], left_count=len(left), right_count=len(right),
                left_minor=left_total, right_minor=right_total, delta_minor=right_total-left_total,
                key_overlap=dict(shared=shared, left_only=len(left)-shared, right_only=len(right)-shared),
                changes=changes, review_groups=groups, next_check=first_order_check(left, right, shared, changes),
                limit="File differences alone cannot establish missing sales, refunds, profit or cause.")
    if review_refunds:
        report["recorded_refunds"] = refund_review(left, right)
    return report


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
    overlap = report["key_overlap"]
    print(f"Order keys in both: {overlap['shared']} | left only: {overlap['left_only']} | right only: {overlap['right_only']}")
    print("First order check:", report["next_check"])
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
    groups = report["review_groups"]
    if groups:
        print("Review across all differing orders (suggested owners):")
        for kind, group in groups.items():
            count = group["count"]
            label = kind.replace("_", " ").capitalize()
            print(f"{label} | {count} {'order' if count == 1 else 'orders'} | increases {money(group['increase_minor'])}, "
                  f"decreases {money(group['decrease_minor'])} | {group['suggested_role']} | {group['next_check']}")
    print(report["limit"])
    if "recorded_refunds" in report:
        refunds = report["recorded_refunds"]
        delta = refunds["comparable_delta_minor"]
        print("Recorded refund change on comparable orders:", money(delta) if delta is not None else "unknown")
        print(f"Comparable: {refunds['comparable']} | amounts changed: {len(refunds['changes'])} | "
              f"matched with blanks: {len(refunds['missing_values'])} | one-sided excluded: {refunds['one_sided']}")
        for item in refunds["changes"][:10]:
            print(f"{item['order']} | left line {item['left_line']}: {money(item['left_minor'])} | "
                  f"right line {item['right_line']}: {money(item['right_minor'])} | change {money(item['delta_minor'])}")
        if refunds["missing_values"] or len(refunds["changes"]) > 10:
            print("Use --json for all changed and blank-value source rows.")
        print(refunds["limit"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--scope-confirmed", action="store_true", help="operator confirmed same store, window, filters and amount definition")
    parser.add_argument("--json", action="store_true", help="write machine-readable evidence to stdout")
    parser.add_argument("--review-refunds", action="store_true", help="compare recorded Refunded Amount on matched Shopify orders")
    args = parser.parse_args()
    try:
        result = compare(args.left, args.right, args.scope_confirmed, args.review_refunds)
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
