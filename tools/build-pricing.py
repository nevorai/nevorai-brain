#!/usr/bin/env python3
"""Writes products/<product>/pricing.md from the LIVE price tables, so a price is never typed by hand.
Reads Kaizen's plans (public.kz_plans, Nevorai OS) and Flow's plan tiers (flow.plan_tiers).
Run: python3 tools/build-pricing.py   (needs psql and the Kaizen vault on this Mac; never prints the password)."""
import json, os, subprocess, datetime, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
pw = subprocess.run(["bash", os.path.expanduser("~/nevorai-kaizen/scripts/vault.sh"), "get", "NEVORAI_OS_DB_PASSWORD"], capture_output=True, text=True).stdout.strip()
if not pw: raise SystemExit("no vault password")
def q(sql):
    r = subprocess.run(["psql", "-h", "aws-0-ap-south-1.pooler.supabase.com", "-p", "5432", "-U", "postgres.wxgfaaaboftzsazknbvl", "-d", "postgres", "-At", "-F", "\t",
                        "-c", "set default_transaction_read_only = on", "-c", sql], capture_output=True, text=True, env={**os.environ, "PGPASSWORD": pw})
    if r.returncode: raise SystemExit(r.stderr)
    return [l.split("\t") for l in r.stdout.splitlines() if l and l != "SET"]
today = datetime.date.today().isoformat()
inr = lambda x: "Rs " + f"{int(round(float(x))):,}".replace(",", ",")
def indian(n):
    n = int(round(float(n))); s = str(n)
    if len(s) <= 3: return s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2: parts.insert(0, head[-2:]); head = head[:-2]
    if head: parts.insert(0, head)
    return ",".join(parts) + "," + tail
rs = lambda x: "Rs " + indian(x)

FOLDER = {"connect": "connect", "flow": "flow", "bookings": "bookings", "courses": "courses", "lpos": "landing-pages", "websites": "websites", "academy": "academy", "agency": "agencies", "tasks": "tasks"}
NAME = {"connect": "Nevorai Connect", "flow": "Nevorai Flow", "bookings": "Nevorai Bookings", "courses": "Nevorai Courses", "lpos": "Nevorai Landing Pages", "websites": "Nevorai Websites", "academy": "Nevorai Academy", "agency": "Nevorai Agencies", "tasks": "Nevorai Tasks"}
rows = q("select product_key, plan_key, name, billing, list_price, gst_mode, coalesce(summary,''), public_buy, coalesce(limits::text,'{}') from public.kz_plans where active and plan_key <> 'test' and coalesce(summary,'') not like 'NOT IN USE%' order by product_key, sort, billing")
by = {}
for p, key, name, billing, price, gst, summary, pub, limits in rows:
    by.setdefault(p, []).append(dict(key=key, name=name, billing=billing, price=float(price), gst=gst, summary=summary, pub=pub == "t", limits=json.loads(limits)))

for p, plans in by.items():
    if p not in FOLDER: continue
    d = ROOT / "products" / FOLDER[p]; d.mkdir(parents=True, exist_ok=True)
    out = [f"# {NAME[p]}: prices", "", f"Last checked: {today} (generated from the live price list by tools/build-pricing.py; do not edit by hand).", "",
           "All prices are in Indian rupees. Prices marked \"+ GST\" have 18% GST added on the invoice.", ""]
    monthly = [x for x in plans if x["billing"] == "monthly" and not x["key"].startswith("topup")]
    yearly = [x for x in plans if x["billing"] == "yearly"]
    topups = [x for x in plans if x["key"].startswith("topup")]
    if monthly:
        out += [f"## {NAME[p]} monthly plans", ""]
        for x in monthly:
            out += [f"### {x['name']}", f"- Price: {rs(x['price'])} per month{' + GST' if x['gst']=='excl' else ' (GST included)'}", f"- What you get: {x['summary']}" if x["summary"] else "", f"- Buy online: {'yes, at billing.nevorai.com' if x['pub'] else 'ask the team'}", ""]
    if yearly:
        out += [f"## {NAME[p]} yearly plans (12 months for the price of 10)", ""]
        for x in yearly:
            out += [f"### {x['name']}", f"- Price: {rs(x['price'])} per year{' + GST' if x['gst']=='excl' else ' (GST included)'}", f"- {x['summary']}" if x["summary"] else "", ""]
    if topups:
        out += [f"## {NAME[p]} top-ups (added to a plan, not sold alone)", ""]
        for x in topups:
            out += [f"- {x['name'].split(': ',1)[-1]}: {rs(x['price'])} per month + GST. {x['summary']}"]
        out += [""]
    out += [f"## Where to pay for {NAME[p]}", "", "Every Nevorai product is paid at billing.nevorai.com (UPI, card or net banking through Razorpay). A GST invoice is sent by email after payment.", ""]
    (d / "pricing.md").write_text("\n".join(l for l in out if l is not None))

# Flow: its own table
tiers = q("select plan_name, monthly_price, yearly_price, daily_views, monthly_views from flow.plan_tiers where is_active and is_base order by display_order")
label = {"starter": "Basic", "growth": "Pro", "leader": "Leader", "enterprise": "Enterprise"}
out = ["# Nevorai Flow: prices", "", f"Last checked: {today} (generated from the live plan table by tools/build-pricing.py; do not edit by hand).", "",
       "All prices are in Indian rupees. Yearly plans save about 2 months. Extra views can be bought any time from the Billing page inside Flow. You can move to a bigger plan any time and pay only the difference. No free trial; the 7-day money-back guarantee covers the first paid plan.", "", "## Nevorai Flow plans", ""]
for name, m, y, dv, mv in tiers:
    views = "Unlimited video views" if int(dv) < 0 else f"{indian(dv)} video views per day ({indian(mv)} a month)"
    out += [f"### {label.get(name, name.title())} plan", f"- Price: {rs(m)} per month, or {rs(y)} per year", f"- Views: {views}", ""]
out += ["## Nevorai Flow links", "", "- All plans: https://flow.nevorai.com/pricing", "- Sign up: https://flow.nevorai.com/auth", ""]
(ROOT / "products" / "flow").mkdir(parents=True, exist_ok=True)
(ROOT / "products" / "flow" / "pricing.md").write_text("\n".join(out))
print("wrote pricing for:", ", ".join(sorted(set(FOLDER[p] for p in by if p in FOLDER) | {"flow"})))
