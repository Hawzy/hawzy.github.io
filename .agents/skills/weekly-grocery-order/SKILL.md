---
name: weekly-grocery-order
description: Fetches the active weekly dinner menu from the blog API, scales and consolidates non-pantry ingredients, checks the idempotency ledger, and prepares or executes grocery cart additions.
---

# Weekly Grocery Order Skill

This skill automates weekly grocery procurement for the recipe blog. It fetches the weekly meal plan from `/api/weekly-menu.json`, mathematically scales ingredient quantities, filters out pantry staples, consolidates common ingredients across recipes, and guards against duplicate cart submissions using an idempotency ledger.

---

## Architecture & Data Flow

```
+--------------------------+
|  /api/weekly-menu.json   | <--- Weekly Menu API Endpoint / Local File
+--------------------------+
             |
             v
+--------------------------+
|   consolidate_menu.py    |
+--------------------------+
      |              |
      |              +--------> Filter out pantry staples (salt, oil, spices)
      |              +--------> Multiply by meal scale factor (e.g. 1.5x)
      |              +--------> Aggregate identical (item, unit) pairs
      v
+--------------------------+
|  .cache/cart_ledger.json | <--- Idempotency check & order fulfillment record
+--------------------------+
      |
      v
+--------------------------+
| Consolidated Cart Output | ---> Clean JSON payload + Human-readable table
+--------------------------+
```

---

## Invocation & CLI Usage

The core engine is located at:
`scripts/consolidate_menu.py` (Python 3 standard library only, zero 3rd-party dependencies).

### Command Syntax

```bash
python .agents/skills/weekly-grocery-order/scripts/consolidate_menu.py [OPTIONS]
```

### CLI Arguments & Flags

| Flag | Default | Description |
|---|---|---|
| `--url <URL_OR_PATH>` | `http://127.0.0.1:4000/api/weekly-menu.json` | URL (`http://`, `https://`, `file://`) or local file path to the weekly menu JSON. If the HTTP server is unreachable, it automatically falls back to `_site/api/weekly-menu.json` if available. |
| `--dry-run` | `False` | Executes full consolidation, prints table and JSON, but **does not modify** the cart ledger file. |
| `--ledger <PATH>` | `.cache/cart_ledger.json` | Path to the JSON idempotency ledger tracking fulfilled weeks. |
| `--force` | `False` | Overrides the duplicate fulfillment check if the current week was already processed. |
| `--json` | `False` | Outputs raw JSON summary only (suppresses ASCII tables), suitable for piping to `jq` or downstream agent scripts. |

---

## Examples

### 1. Dry Run Preview (Safe Inspection)
```bash
python .agents/skills/weekly-grocery-order/scripts/consolidate_menu.py --dry-run
```
Output includes:
- Consolidated shopping cart with summed quantities, categories, and retailer UPCs.
- Skipped pantry staples with scale-adjusted quantities.
- Warnings if the target week was previously fulfilled.

### 2. Live Fulfillment (Records to Ledger)
```bash
python .agents/skills/weekly-grocery-order/scripts/consolidate_menu.py
```
Updates `.cache/cart_ledger.json` with timestamp, item count, and cart items.

### 3. Processing a Static File or Build Artifact
```bash
python .agents/skills/weekly-grocery-order/scripts/consolidate_menu.py --url _site/api/weekly-menu.json --dry-run
```

### 4. Overriding Previous Fulfillment
```bash
python .agents/skills/weekly-grocery-order/scripts/consolidate_menu.py --force
```

---

## Idempotency Rules

1. Before fulfilling an order, the engine checks `.cache/cart_ledger.json` for key `<week_of>`.
2. **In `--dry-run` mode**: If `<week_of>` exists, emits a non-fatal warning:
   `[IDEMPOTENCY WARNING] Week of YYYY-MM-DD was previously fulfilled at <timestamp>`
3. **In live mode**: If `<week_of>` exists, halts execution with exit code `2` (`AlreadyFulfilledError`) unless `--force` is provided.
4. On successful live fulfillment, the ledger is updated atomically with the UTC timestamp and final line items.
