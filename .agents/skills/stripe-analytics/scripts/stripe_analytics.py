#!/usr/bin/env python3
"""
Stripe analytics script - fetches operational metrics from api.stripe.com.
No third-party proxy or SDK dependency. Python stdlib only.
"""
import argparse
import datetime
import json
import os
import sys
import urllib.parse
import urllib.request

BASE_URL = "https://api.stripe.com/v1"
CONFIG_DIR = os.path.expanduser("~/.config/stripe-analytics")
ENV_PATH = os.path.join(CONFIG_DIR, ".env")

# Module-level timezone (set by --tz CLI arg, default CST/UTC+8)
_TZ = datetime.timezone(datetime.timedelta(hours=8))

_TZ_ALIASES = {"CST": 8, "UTC": 0, "EST": -5, "PST": -8, "JST": 9, "CET": 1, "AEST": 10}


def parse_tz(tz_str):
    """Parse timezone string like '+8', '-5', 'CST', 'UTC'."""
    s = tz_str.strip().upper()
    if s in _TZ_ALIASES:
        return datetime.timezone(datetime.timedelta(hours=_TZ_ALIASES[s]))
    try:
        return datetime.timezone(datetime.timedelta(hours=float(s)))
    except ValueError:
        print(f"Invalid timezone: {tz_str}. Use offset like '+8' or alias: {', '.join(_TZ_ALIASES)}")
        sys.exit(1)


# ──────────────────────────────────────────────────────────
# Configuration & Auth
# ──────────────────────────────────────────────────────────

def load_config():
    """Load Stripe credentials from env file, falling back to environment variable."""
    if os.path.exists(ENV_PATH):
        config = {}
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[7:]
                if "=" in line:
                    key, val = line.split("=", 1)
                    config[key.strip()] = val.strip().strip('"').strip("'")
        if "STRIPE_SECRET_KEY" in config:
            return config

    # Fallback: check environment variable
    key = os.environ.get("STRIPE_SECRET_KEY")
    if key:
        return {"STRIPE_SECRET_KEY": key}

    print(json.dumps({
        "error": "no_credentials",
        "message": "Stripe credentials not found. Run 'setup' first or set STRIPE_SECRET_KEY env var.",
        "setup_hint": "python3 stripe_analytics.py setup --key sk_live_...",
    }))
    sys.exit(1)


def stripe_request(method, path, api_key, params=None, data=None):
    url = f"{BASE_URL}/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read()
        try:
            error = json.loads(err_body)
            msg = error.get("error", {}).get("message", str(error))
        except Exception:
            msg = err_body.decode(errors="replace")
        print(json.dumps({"error": "api_error", "status": e.code, "detail": msg}))
        sys.exit(1)
    except urllib.error.URLError as e:
        print(json.dumps({"error": "network_error", "detail": str(e.reason)}))
        sys.exit(1)


def fetch_all(resource, api_key, params=None, max_items=500):
    """Paginate through all results up to max_items."""
    if params is None:
        params = {}
    params["limit"] = min(100, max_items)
    items = []
    while len(items) < max_items:
        result = stripe_request("GET", resource, api_key, params=params)
        batch = result.get("data", [])
        if not batch:
            break
        items.extend(batch)
        if not result.get("has_more"):
            break
        params["starting_after"] = batch[-1]["id"]
    return items[:max_items]


# ──────────────────────────────────────────────────────────
# Formatting helpers
# ──────────────────────────────────────────────────────────

def ts(dt):
    return int(dt.timestamp())


def parse_date(s):
    return datetime.datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=_TZ)


def date_range(args):
    now = datetime.datetime.now(_TZ)
    if args.start:
        start = parse_date(args.start)
    else:
        start = now - datetime.timedelta(days=args.days)
    end = parse_date(args.end) if args.end else now
    return ts(start), ts(end)


def fmt_money(cents, currency="usd"):
    if currency.lower() in ("jpy", "krw"):
        return f"{cents:,} {currency.upper()}"
    return f"{cents / 100:,.2f} {currency.upper()}"


def fmt_date(unix_ts):
    return datetime.datetime.fromtimestamp(unix_ts, tz=_TZ).strftime("%Y-%m-%d")


def fmt_pct(value):
    return f"{value:.1f}%"


def print_kv(pairs, title=None):
    if title:
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}")
    max_key = max(len(k) for k, _ in pairs) if pairs else 0
    for k, v in pairs:
        print(f"  {k:<{max_key + 2}} {v}")
    print()


def print_table(rows, headers):
    if not rows:
        print("  No data.")
        return
    widths = [max(len(str(h)), max((len(str(r[i])) for r in rows), default=0))
              for i, h in enumerate(headers)]
    sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    hdr = "| " + " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers)) + " |"
    print(sep)
    print(hdr)
    print(sep)
    for row in rows:
        print("| " + " | ".join(str(row[i]).ljust(widths[i]) for i, _ in enumerate(headers)) + " |")
    print(sep)


# ──────────────────────────────────────────────────────────
# MRR calculation helpers
# ──────────────────────────────────────────────────────────

def item_mrr_cents(item):
    """Calculate monthly recurring revenue contribution from a subscription item."""
    price = item.get("price", {})
    amount = price.get("unit_amount", 0) or 0
    interval = price.get("recurring", {}).get("interval", "month")
    qty = item.get("quantity", 1)
    if interval == "year":
        return (amount * qty) // 12
    elif interval == "month":
        return amount * qty
    elif interval == "week":
        return amount * qty * 4
    elif interval == "day":
        return amount * qty * 30
    return 0


def sub_has_paid(sub):
    """Check if a subscription has actually been paid (latest invoice amount_paid > 0).

    When latest_invoice is expanded via API, it's a dict with amount_paid.
    If not expanded (just an ID string), fall back to assuming paid.
    """
    invoice = sub.get("latest_invoice")
    if isinstance(invoice, dict):
        return invoice.get("amount_paid", 0) > 0
    return True


# ──────────────────────────────────────────────────────────
# Setup & Check commands (self-contained, no pre-existing config needed)
# ──────────────────────────────────────────────────────────

def cmd_setup(args):
    """Validate Stripe key, save to ~/.config/stripe-analytics/.env."""
    key = args.key or os.environ.get("STRIPE_SETUP_KEY")
    if not key:
        print(json.dumps({
            "error": "no_key",
            "message": "Provide --key or set STRIPE_SETUP_KEY env var.",
        }))
        sys.exit(1)

    # Validate by calling /v1/balance (lightweight, available on all keys)
    try:
        result = stripe_request("GET", "balance", key)
    except SystemExit:
        print(json.dumps({
            "error": "auth_failed",
            "message": "Invalid Stripe key. Check your key at https://dashboard.stripe.com/apikeys",
        }))
        sys.exit(1)

    # Determine key type
    key_type = "test" if key.startswith("sk_test_") else "live"

    # Write env file
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(ENV_PATH, "w") as f:
        f.write(f"STRIPE_SECRET_KEY={key}\n")
    os.chmod(ENV_PATH, 0o600)

    # Extract account info from balance
    available = result.get("available", [])
    pending = result.get("pending", [])

    print(json.dumps({
        "status": "ok",
        "key_type": key_type,
        "env_path": ENV_PATH,
        "balance": {
            "available": [{"amount": a["amount"], "currency": a["currency"]} for a in available],
            "pending": [{"amount": p["amount"], "currency": p["currency"]} for p in pending],
        },
    }, indent=2))


def cmd_check(args):
    """Verify saved credentials work."""
    config = load_config()
    key = config["STRIPE_SECRET_KEY"]
    result = stripe_request("GET", "balance", key)
    key_type = "test" if key.startswith("sk_test_") else "live"

    available = result.get("available", [])
    print(json.dumps({
        "status": "ok",
        "key_type": key_type,
        "env_path": ENV_PATH if os.path.exists(ENV_PATH) else "env_var",
        "balance_available": [{"amount": a["amount"], "currency": a["currency"]} for a in available],
    }, indent=2))


# ──────────────────────────────────────────────────────────
# Analytics commands
# ──────────────────────────────────────────────────────────

def cmd_revenue(args, api_key):
    start, end = date_range(args)
    params = {"created[gte]": start, "created[lte]": end}

    charges = fetch_all("charges", api_key, params, max_items=args.max_items)
    succeeded = [c for c in charges if c.get("status") == "succeeded" and not c.get("refunded")]

    total = sum(c["amount"] for c in succeeded)
    currencies = {}
    for c in succeeded:
        cur = c.get("currency", "usd")
        currencies[cur] = currencies.get(cur, 0) + c["amount"]

    days_span = max((end - start) / 86400, 1)

    print_kv([
        ("Period", f"{fmt_date(start)} ~ {fmt_date(end)} ({int(days_span)} days)"),
        ("Total charges", str(len(charges))),
        ("Succeeded", str(len(succeeded))),
        ("Failed / Refunded", str(len(charges) - len(succeeded))),
    ], "Revenue Overview")

    for cur, amt in sorted(currencies.items()):
        print_kv([
            ("Total revenue", fmt_money(amt, cur)),
            ("Daily average", fmt_money(int(amt / days_span), cur)),
            ("Avg per charge", fmt_money(int(amt / len(succeeded)) if succeeded else 0, cur)),
        ], f"Revenue ({cur.upper()})")

    if not args.no_daily:
        daily = {}
        for c in succeeded:
            day = fmt_date(c["created"])
            cur = c.get("currency", "usd")
            if day not in daily:
                daily[day] = {"count": 0, "amount": 0, "currency": cur}
            daily[day]["count"] += 1
            daily[day]["amount"] += c["amount"]

        rows = []
        for day in sorted(daily.keys()):
            d = daily[day]
            rows.append([day, str(d["count"]), fmt_money(d["amount"], d["currency"])])
        print(f"\n  Daily Breakdown")
        print(f"  {'-' * 40}")
        print_table(rows, ["Date", "Charges", "Revenue"])

    if args.json:
        print(json.dumps({
            "period": {"start": fmt_date(start), "end": fmt_date(end)},
            "total_charges": len(charges),
            "succeeded": len(succeeded),
            "revenue_by_currency": {k: v for k, v in currencies.items()},
            "daily_avg_cents": {k: int(v / days_span) for k, v in currencies.items()},
        }, indent=2))


def cmd_customers(args, api_key):
    start, end = date_range(args)
    params = {"created[gte]": start, "created[lte]": end}
    customers = fetch_all("customers", api_key, params, max_items=args.max_items)

    weekly = {}
    for c in customers:
        dt = datetime.datetime.fromtimestamp(c["created"], tz=_TZ)
        week_start = dt - datetime.timedelta(days=dt.weekday())
        key = week_start.strftime("%Y-%m-%d")
        weekly[key] = weekly.get(key, 0) + 1

    print_kv([
        ("Period", f"{fmt_date(start)} ~ {fmt_date(end)}"),
        ("New customers", str(len(customers))),
    ], "Customer Growth")

    if weekly:
        rows = [[wk, str(cnt)] for wk, cnt in sorted(weekly.items())]
        print(f"\n  Weekly New Customers")
        print(f"  {'-' * 40}")
        print_table(rows, ["Week of", "New Customers"])

    if args.json:
        print(json.dumps({
            "period": {"start": fmt_date(start), "end": fmt_date(end)},
            "new_customers": len(customers),
            "weekly_cohorts": dict(sorted(weekly.items())),
        }, indent=2))


def cmd_subscriptions(args, api_key):
    subs = fetch_all("subscriptions", api_key, {"status": "all", "limit": 100, "expand[]": "data.latest_invoice"}, max_items=args.max_items)

    by_status = {}
    mrr_cents = 0
    for s in subs:
        st = s.get("status", "unknown")
        by_status[st] = by_status.get(st, 0) + 1
        if st == "active" and sub_has_paid(s):
            for item in s.get("items", {}).get("data", []):
                mrr_cents += item_mrr_cents(item)

    active = by_status.get("active", 0)
    trialing = by_status.get("trialing", 0)
    canceled = by_status.get("canceled", 0)
    past_due = by_status.get("past_due", 0)
    total = len(subs)

    print_kv([
        ("Total subscriptions", str(total)),
        ("Active", str(active)),
        ("Trialing", str(trialing)),
        ("Past due", str(past_due)),
        ("Canceled", str(canceled)),
    ], "Subscription Overview")

    print_kv([
        ("MRR (Monthly Recurring Revenue)", fmt_money(mrr_cents)),
        ("ARR (Annual Recurring Revenue)", fmt_money(mrr_cents * 12)),
    ], "Recurring Revenue")

    now = datetime.datetime.now(_TZ)
    thirty_days_ago = ts(now - datetime.timedelta(days=30))
    recent_canceled = [s for s in subs
                       if s.get("status") == "canceled"
                       and s.get("canceled_at", 0) and s["canceled_at"] >= thirty_days_ago]

    if active + len(recent_canceled) > 0:
        churn_rate = len(recent_canceled) / (active + len(recent_canceled)) * 100
    else:
        churn_rate = 0

    print_kv([
        ("Canceled (last 30d)", str(len(recent_canceled))),
        ("Churn rate (30d)", fmt_pct(churn_rate)),
    ], "Churn (Last 30 Days)")

    if args.json:
        print(json.dumps({
            "total": total,
            "by_status": by_status,
            "mrr_cents": mrr_cents,
            "arr_cents": mrr_cents * 12,
            "churn_30d": len(recent_canceled),
            "churn_rate_30d": round(churn_rate, 2),
        }, indent=2))


def cmd_refunds(args, api_key):
    start, end = date_range(args)
    params = {"created[gte]": start, "created[lte]": end}

    refunds = fetch_all("refunds", api_key, params, max_items=args.max_items)
    charges = fetch_all("charges", api_key, params, max_items=args.max_items)
    succeeded_charges = [c for c in charges if c.get("status") == "succeeded"]

    total_refund_amount = sum(r.get("amount", 0) for r in refunds)
    total_charge_amount = sum(c.get("amount", 0) for c in succeeded_charges)

    by_reason = {}
    for r in refunds:
        reason = r.get("reason") or "not_specified"
        by_reason[reason] = by_reason.get(reason, 0) + 1

    refund_rate = (len(refunds) / len(succeeded_charges) * 100) if succeeded_charges else 0
    amount_rate = (total_refund_amount / total_charge_amount * 100) if total_charge_amount else 0

    print_kv([
        ("Period", f"{fmt_date(start)} ~ {fmt_date(end)}"),
        ("Total refunds", str(len(refunds))),
        ("Total charges", str(len(succeeded_charges))),
        ("Refund rate (count)", fmt_pct(refund_rate)),
        ("Refund amount", fmt_money(total_refund_amount)),
        ("Charge amount", fmt_money(total_charge_amount)),
        ("Refund rate (amount)", fmt_pct(amount_rate)),
    ], "Refund Overview")

    if by_reason:
        rows = [[reason, str(cnt)] for reason, cnt in sorted(by_reason.items(), key=lambda x: -x[1])]
        print(f"\n  Refund Reasons")
        print(f"  {'-' * 40}")
        print_table(rows, ["Reason", "Count"])

    if args.json:
        print(json.dumps({
            "period": {"start": fmt_date(start), "end": fmt_date(end)},
            "refunds": len(refunds),
            "charges": len(succeeded_charges),
            "refund_rate_pct": round(refund_rate, 2),
            "refund_amount_cents": total_refund_amount,
            "charge_amount_cents": total_charge_amount,
            "by_reason": by_reason,
        }, indent=2))


def cmd_products(args, api_key):
    start, end = date_range(args)
    params = {"created[gte]": start, "created[lte]": end}
    charges = fetch_all("charges", api_key, params, max_items=args.max_items)
    succeeded = [c for c in charges if c.get("status") == "succeeded"]

    products = fetch_all("products", api_key, {}, max_items=200)
    product_map = {p["id"]: p.get("name", p["id"]) for p in products}

    invoices_params = {"created[gte]": start, "created[lte]": end}
    invoices = fetch_all("invoices", api_key, invoices_params, max_items=args.max_items)

    product_revenue = {}
    for inv in invoices:
        if inv.get("status") != "paid":
            continue
        lines = inv.get("lines", {}).get("data", [])
        for line in lines:
            price = line.get("price", {})
            prod_id = price.get("product", "unknown")
            prod_name = product_map.get(prod_id, prod_id)
            amount = line.get("amount", 0)
            if prod_name not in product_revenue:
                product_revenue[prod_name] = {"amount": 0, "count": 0}
            product_revenue[prod_name]["amount"] += amount
            product_revenue[prod_name]["count"] += 1

    print_kv([
        ("Period", f"{fmt_date(start)} ~ {fmt_date(end)}"),
        ("Total succeeded charges", str(len(succeeded))),
        ("Total revenue", fmt_money(sum(c["amount"] for c in succeeded))),
    ], "Product Performance")

    if product_revenue:
        rows = []
        for name, data in sorted(product_revenue.items(), key=lambda x: -x[1]["amount"]):
            rows.append([name, str(data["count"]), fmt_money(data["amount"])])
        print_table(rows, ["Product", "Invoices", "Revenue"])

    if args.json:
        print(json.dumps({
            "period": {"start": fmt_date(start), "end": fmt_date(end)},
            "total_charges": len(succeeded),
            "product_revenue": product_revenue,
        }, indent=2))


def cmd_overview(args, api_key):
    start, end = date_range(args)

    print(f"\n{'#' * 60}")
    print(f"  STRIPE OPERATIONAL OVERVIEW")
    print(f"  {fmt_date(start)} ~ {fmt_date(end)}")
    print(f"{'#' * 60}")

    # Revenue
    params = {"created[gte]": start, "created[lte]": end}
    charges = fetch_all("charges", api_key, params, max_items=args.max_items)
    succeeded = [c for c in charges if c.get("status") == "succeeded" and not c.get("refunded")]
    failed = [c for c in charges if c.get("status") == "failed"]
    total_revenue = sum(c["amount"] for c in succeeded)
    days_span = max((end - start) / 86400, 1)
    success_rate = (len(succeeded) / len(charges) * 100) if charges else 0

    print_kv([
        ("Total revenue", fmt_money(total_revenue)),
        ("Daily average", fmt_money(int(total_revenue / days_span))),
        ("Charges (succeeded/total)", f"{len(succeeded)}/{len(charges)}"),
        ("Success rate", fmt_pct(success_rate)),
    ], "Revenue")

    # Customers
    customers = fetch_all("customers", api_key, params, max_items=args.max_items)
    print_kv([
        ("New customers (period)", str(len(customers))),
    ], "Customers")

    # Subscriptions
    subs = fetch_all("subscriptions", api_key, {"status": "all", "limit": 100, "expand[]": "data.latest_invoice"}, max_items=args.max_items)
    active = sum(1 for s in subs if s.get("status") == "active")
    trialing = sum(1 for s in subs if s.get("status") == "trialing")
    canceled = sum(1 for s in subs if s.get("status") == "canceled")

    mrr = 0
    for s in subs:
        if s.get("status") != "active":
            continue
        if not sub_has_paid(s):
            continue
        for item in s.get("items", {}).get("data", []):
            mrr += item_mrr_cents(item)

    print_kv([
        ("Active", str(active)),
        ("Trialing", str(trialing)),
        ("Canceled", str(canceled)),
        ("MRR", fmt_money(mrr)),
        ("ARR", fmt_money(mrr * 12)),
    ], "Subscriptions")

    # Refunds
    refunds = fetch_all("refunds", api_key, params, max_items=args.max_items)
    refund_amount = sum(r.get("amount", 0) for r in refunds)
    refund_rate = (len(refunds) / len(succeeded) * 100) if succeeded else 0
    print_kv([
        ("Refunds", str(len(refunds))),
        ("Refund amount", fmt_money(refund_amount)),
        ("Refund rate", fmt_pct(refund_rate)),
    ], "Refunds")

    # Payment health
    print_kv([
        ("Succeeded", str(len(succeeded))),
        ("Failed", str(len(failed))),
        ("Success rate", fmt_pct(success_rate)),
    ], "Payment Health")


def cmd_balance(args, api_key):
    start, end = date_range(args)
    params = {"created[gte]": start, "created[lte]": end}
    txns = fetch_all("balance_transactions", api_key, params, max_items=args.max_items)

    by_type = {}
    total_gross = 0
    total_fee = 0
    total_net = 0
    for t in txns:
        typ = t.get("type", "unknown")
        amt = t.get("amount", 0)
        fee = t.get("fee", 0)
        net = t.get("net", 0)
        if typ not in by_type:
            by_type[typ] = {"count": 0, "gross": 0, "fee": 0, "net": 0}
        by_type[typ]["count"] += 1
        by_type[typ]["gross"] += amt
        by_type[typ]["fee"] += fee
        by_type[typ]["net"] += net
        total_gross += amt
        total_fee += fee
        total_net += net

    print_kv([
        ("Period", f"{fmt_date(start)} ~ {fmt_date(end)}"),
        ("Total transactions", str(len(txns))),
        ("Gross", fmt_money(total_gross)),
        ("Fees", fmt_money(total_fee)),
        ("Net", fmt_money(total_net)),
        ("Fee rate", fmt_pct(total_fee / total_gross * 100) if total_gross else "N/A"),
    ], "Balance Summary")

    if by_type:
        rows = []
        for typ, d in sorted(by_type.items(), key=lambda x: -abs(x[1]["gross"])):
            rows.append([typ, str(d["count"]), fmt_money(d["gross"]), fmt_money(d["fee"]), fmt_money(d["net"])])
        print(f"\n  Breakdown by Type")
        print(f"  {'-' * 40}")
        print_table(rows, ["Type", "Count", "Gross", "Fees", "Net"])

    if args.json:
        print(json.dumps({
            "period": {"start": fmt_date(start), "end": fmt_date(end)},
            "total_transactions": len(txns),
            "gross_cents": total_gross,
            "fee_cents": total_fee,
            "net_cents": total_net,
            "by_type": by_type,
        }, indent=2))


def cmd_mrr_trend(args, api_key):
    subs = fetch_all("subscriptions", api_key, {"status": "all", "limit": 100, "expand[]": "data.latest_invoice"}, max_items=args.max_items)

    monthly = {}
    for s in subs:
        if s.get("status") not in ("active", "canceled", "past_due"):
            continue
        start_dt = datetime.datetime.fromtimestamp(s["created"], tz=_TZ)
        month_key = start_dt.strftime("%Y-%m")
        if month_key not in monthly:
            monthly[month_key] = {"new": 0, "canceled": 0, "mrr_new": 0}
        monthly[month_key]["new"] += 1

        if s.get("status") == "canceled" and s.get("canceled_at"):
            cancel_dt = datetime.datetime.fromtimestamp(s["canceled_at"], tz=_TZ)
            cancel_key = cancel_dt.strftime("%Y-%m")
            if cancel_key not in monthly:
                monthly[cancel_key] = {"new": 0, "canceled": 0, "mrr_new": 0}
            monthly[cancel_key]["canceled"] += 1

        if sub_has_paid(s):
            for item in s.get("items", {}).get("data", []):
                monthly[month_key]["mrr_new"] += item_mrr_cents(item)

    print_kv([
        ("Total subscriptions analyzed", str(len(subs))),
    ], "MRR Trend")

    if monthly:
        rows = []
        for month in sorted(monthly.keys()):
            d = monthly[month]
            rows.append([month, str(d["new"]), str(d["canceled"]),
                         str(d["new"] - d["canceled"]), fmt_money(d["mrr_new"])])
        print_table(rows, ["Month", "New", "Canceled", "Net", "New MRR"])

    if args.json:
        print(json.dumps({"monthly": dict(sorted(monthly.items()))}, indent=2))


# ──────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Stripe operational analytics")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--max-items", type=int, default=500, help="Max items to fetch per resource")
    parser.add_argument("--tz", default="CST", help="Timezone for dates (default: CST/UTC+8). Offset like '+8'/'-5' or alias: CST, UTC, EST, PST, JST")
    sub = parser.add_subparsers(dest="command")

    def add_date_args(p):
        p.add_argument("--days", type=int, default=30, help="Look back N days (default: 30)")
        p.add_argument("--start", help="Start date YYYY-MM-DD")
        p.add_argument("--end", help="End date YYYY-MM-DD")

    # setup (self-contained, no config needed)
    setup_p = sub.add_parser("setup", help="Save Stripe key and verify it works")
    setup_p.add_argument("--key", help="Stripe secret key (or set STRIPE_SETUP_KEY env var)")

    # check (needs config)
    sub.add_parser("check", help="Verify saved credentials work")

    # Analytics commands
    ov = sub.add_parser("overview", help="Full operational dashboard")
    add_date_args(ov)

    rev = sub.add_parser("revenue", help="Revenue analytics")
    add_date_args(rev)
    rev.add_argument("--no-daily", action="store_true", help="Skip daily breakdown")

    cust = sub.add_parser("customers", help="Customer growth analytics")
    add_date_args(cust)

    sub.add_parser("subscriptions", help="Subscription & MRR analytics")

    ref = sub.add_parser("refunds", help="Refund analytics")
    add_date_args(ref)

    prod = sub.add_parser("products", help="Product performance")
    add_date_args(prod)

    bal = sub.add_parser("balance", help="Balance transactions & fee breakdown")
    add_date_args(bal)

    sub.add_parser("mrr-trend", help="MRR trend by month")

    args = parser.parse_args()

    global _TZ
    _TZ = parse_tz(args.tz)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Setup is self-contained
    if args.command == "setup":
        cmd_setup(args)
        return

    # Check needs config but handles its own flow
    if args.command == "check":
        cmd_check(args)
        return

    # All other commands: load config, extract key, dispatch
    config = load_config()
    api_key = config["STRIPE_SECRET_KEY"]

    dispatch = {
        "overview": cmd_overview,
        "revenue": cmd_revenue,
        "customers": cmd_customers,
        "subscriptions": cmd_subscriptions,
        "refunds": cmd_refunds,
        "products": cmd_products,
        "balance": cmd_balance,
        "mrr-trend": cmd_mrr_trend,
    }
    dispatch[args.command](args, api_key)


if __name__ == "__main__":
    main()
