#!/usr/bin/env python3
"""Fails when a file has no "Last checked" line, a rupee price appears outside a pricing.md, or the repo passes 60 files (Connect reads at most 60 per source)."""
import pathlib, re, sys
root = pathlib.Path(__file__).resolve().parent.parent
files = [p for p in root.rglob("*.md") if ".git" not in p.parts]
bad = []
price = re.compile(r"(Rs\.?|₹)\s?\d[\d,]{2,}")
ALLOW = {"objections/common.md", "ads/connect-switch-offer.md", "company/policies.md", "compare/whatsapp-tools.md", "tests/questions.md", "products/connect/overview.md", "products/connect/limits-and-issues.md"}
for p in files:
    rel = p.relative_to(root).as_posix()
    text = p.read_text()
    if rel != "README.md" and "Last checked:" not in text: bad.append(f"{rel}: no 'Last checked' line")
    if not rel.endswith("pricing.md") and rel not in ALLOW and price.search(text): bad.append(f"{rel}: a price outside pricing.md")
# Connect reads at most 60 files per source, so the repo is added as TWO sources: /products and the rest.
prod = [p for p in files if p.relative_to(root).parts[0] == "products"]
rest = [p for p in files if p.relative_to(root).parts[0] not in ("products", "tools")]
if len(prod) > 60: bad.append(f"products/: {len(prod)} files, more than 60 (split into a third source)")
if len(rest) > 60: bad.append(f"outside products/: {len(rest)} files, more than 60")
print(f"{len(files)} files checked")
for b in bad: print("FAIL", b)
sys.exit(1 if bad else 0)
