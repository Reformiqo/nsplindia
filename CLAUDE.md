# CLAUDE.md — Nelito Finance (nelito_finance)

## Project Overview

**App**: `nelito_finance` — a Frappe/ERPNext v16 custom app for Nelito Systems Pvt. Ltd.
**Repository**: Reformiqo/nsplindia
**Purpose**: Revenue Management, Project Accounting, and Milestone Billing
**Client**: Nelito Systems Pvt. Ltd. (subsidiary of DTS Corporation, Japan)
**Industry**: BFSI software products & services (FinCraft Core Banking, ILMS, Regulatory Reporting)
**Revenue Streams**: License, Implementation, AMC, T&M, Travel, Recurring

## Tech Stack

- **Framework**: Frappe v16 + ERPNext v16
- **Backend**: Python 3.11+, MariaDB 10.6+
- **Frontend**: Frappe Client JS (not React/Vue)
- **Task Queue**: Redis Queue (RQ)
- **India Compliance**: india_compliance app (GST, e-Invoice, TDS)

## File Structure

```
nelito_finance/
├── nelito_finance/
│   ├── __init__.py                  # App version
│   ├── hooks.py                     # Doc events, scheduler, fixtures, after_install
│   ├── install.py                   # Auto-creates 23 custom fields on install
│   ├── modules.txt                  # "Nelito Finance"
│   ├── doctype/
│   │   ├── order_review_form/       # Main DocType (submittable)
│   │   │   ├── order_review_form.json     # 20 fields, autoname ORF-YYYY-####
│   │   │   ├── order_review_form.py       # Controller: on_submit → auto-creates SO + Projects + Tasks
│   │   │   ├── order_review_form.js       # Client: total calc, view buttons
│   │   │   └── test_order_review_form.py  # Unit tests
│   │   └── orf_item/                # Child table (8 fields)
│   │       ├── orf_item.json
│   │       └── orf_item.py          # Amount calc, milestone_split validation
│   ├── api/
│   │   ├── task_hooks.py            # Billing calc, milestone → Sales Invoice, warranty
│   │   ├── project_hooks.py         # Parent project value auto-sum
│   │   ├── expense_hooks.py         # Billable expense → Sales Invoice
│   │   ├── scheduled_jobs.py        # Daily billing sync, yearly AMC renewal
│   │   └── utils.py                 # get_sub_projects, get_milestone_summary, get_contract_summary
│   ├── report/
│   │   ├── contract_overview/       # Script Report: parent contract grouping
│   │   └── milestone_billing_tracker/  # Script Report: task milestone listing
│   ├── public/js/
│   │   └── project_custom.js        # Task: Create Invoice btn, billing toggle; Project: sub-PID dashboard
│   ├── config/
│   │   └── desktop.py               # Module card config
│   └── templates/
├── setup.py
├── setup.cfg
└── requirements.txt
```

## Architecture Rules

1. **Never use `frappe.db.commit()` inside document controllers** — Frappe handles transactions automatically
2. **Use `frappe.throw()` for user-facing errors**, `frappe.log_error()` for debug logging
3. **Always set `flags.ignore_permissions = True`** when auto-creating docs from hooks
4. **Custom fields use `custom_` prefix** — mandatory ERPNext v16 convention
5. **DocType JSON files must be valid** — run `bench migrate` after any JSON change
6. **All whitelisted APIs need `@frappe.whitelist()` decorator**
7. **Client scripts use `frappe.ui.form.on("DocType", {...})` pattern**
8. **hooks.py doc_events use dotted path**: `"nelito_finance.api.module.function_name"`

## Key Custom Fields (23 total, defined in install.py)

### On Project (7 fields)
- `custom_master_contract_id` (Data) — Root PID grouping e.g., PID_2627_0001
- `custom_parent_project` (Link→Project) — Links sub-PID to parent
- `custom_revenue_category` (Select) — License|Implementation|AMC|T&M|Recurring|Travel|Other
- `custom_line_value` (Currency) — Contract value for this PID line
- `custom_total_contract_value` (Currency, read-only) — Auto-sum of children
- `custom_warranty_start` (Date)
- `custom_warranty_end` (Date)

### On Task (5 fields)
- `custom_billing_percentage` (Percent) — e.g., 30, 15, 20
- `custom_billing_amount` (Currency, read-only) — line_value x billing_%
- `custom_billing_status` (Select) — Not Yet Due|Chargeable|Partially Invoiced|Fully Invoiced|On Hold
- `custom_phase` (Select) — Phase 1|Phase 2|Phase 3|N/A
- `custom_linked_invoice` (Link→Sales Invoice, read-only)

### On Sales Invoice (4 fields)
- `custom_transaction_origin` (Select) — Milestone|Time & Material|Recurring|Ad-hoc|Credit Note
- `custom_master_contract_id` (Data)
- `custom_linked_milestone_task` (Link→Task, read-only)
- `custom_service_period_from` (Date)

### On Sales Order Item (3 fields)
- `custom_revenue_category`, `custom_linked_project`, `custom_line_value`

### On Customer (1 field)
- `custom_master_contract_ids` (Small Text)

### On Sales Order (1 field)
- `custom_master_contract_id` (Data)

### On Expense Claim (2 fields)
- `custom_billable_to_client` (Check), `custom_linked_sales_invoice` (Link→Sales Invoice)

## Naming Conventions

- **PID Format**: `PID_{FY}_{SEQ}-{LINE}` → e.g., PID_2627_0001-00 (parent), PID_2627_0001-01 (license sub)
- **ORF Format**: `ORF-YYYY-####` → e.g., ORF-2026-0001
- **Items**: `SVC-{CATEGORY}` → e.g., SVC-LICENSE, SVC-IMPLEMENTATION, SVC-AMC

## Key Workflows

### Order Review Form (ORF) Submission
1. User fills ORF with customer, contract ID, line items (with optional milestone splits)
2. On submit: auto-creates Sales Order → Parent Project (PID-00) → Sub-Projects (PID-01, PID-02...) → Milestone Tasks
3. Links are stored back on the ORF (sales_order, parent_project fields)

### Milestone Billing
1. Task marked Completed + billing_status set to "Chargeable"
2. `task_hooks.on_task_update` auto-creates Sales Invoice
3. Invoice linked back to task via `custom_linked_invoice`
4. Billing status updated to "Fully Invoiced"

### Daily Billing Sync (Scheduled)
- Recalculates `custom_billing_amount` for all active tasks (keeps amounts in sync if line values change)

### Yearly AMC Renewal (Scheduled)
- Finds AMC projects nearing warranty_end, creates renewal projects for the next year

### Billable Expense Claims
- On submit of Expense Claim with `custom_billable_to_client` checked: auto-creates Sales Invoice

## Testing Commands

```bash
bench --site SITE run-tests --app nelito_finance
bench --site SITE run-tests --module nelito_finance.doctype.order_review_form.test_order_review_form
bench --site SITE console
```

## Common Bench Commands

```bash
bench --site SITE migrate           # Apply DocType changes
bench --site SITE clear-cache       # Clear redis cache
bench build                          # Rebuild JS/CSS assets
bench --site SITE console           # Python shell with frappe context
bench --site SITE set-config developer_mode 1
```

## Development Workflow

### Branch Strategy
- **Default branch**: `main`
- Feature branches should follow descriptive naming conventions
- Always create pull requests for code review before merging to `main`

### Git Conventions
- Write clear, descriptive commit messages in imperative mood
- Keep commits focused — one logical change per commit
- Do not force-push to shared branches

## Frappe v16 Compatibility Rules

These rules are **mandatory** for all code in this app:

### Python
- **Never call `frappe.db.commit()`** inside doc_events hooks or scheduled jobs — Frappe v16 raises an error. Frappe manages transactions automatically.
- **Use `frappe.log_error(message=..., title=...)`** with keyword arguments — positional args are deprecated in v16.
- **Test base class**: Use `from frappe.tests import IntegrationTestCase` (not `FrappeTestCase` which is removed in v16). Use `UnitTestCase` for pure logic tests without DB.
- **No raw SQL in `frappe.get_all()` fields**: Use dict syntax for aggregates: `{"SUM": "field", "as": "alias"}` instead of `"sum(field) as alias"`.
- **Default sort is `creation` not `modified`**: If you need `modified` ordering, specify it explicitly with `order_by`.
- **`frappe.flags.in_test` is deprecated**: Use `frappe.in_test` instead.
- **`has_permission` hooks must return explicit `True`**: Returning `None` or other truthy values no longer grants permission.

### JavaScript
- **v16 loads JS as IIFEs**: Never declare bare `function` at module level. Use `frappe.provide("frappe.nelito_finance")` and attach functions to the namespace.
- **Use `frappe.format(value, {fieldtype: "Currency"})`** instead of bare `format_currency()` for reliable currency formatting.
- **No global variable pollution**: If you must set globals, assign to `window.varName` explicitly.

### DocType JSON
- `is_submittable`, `istable`, `autoname` format patterns — all remain valid in v16.
- Default sort changed to `creation` — set `sort_field` explicitly if needed.

## Conventions for AI Assistants

- Read existing code before proposing changes
- Do not create files unless necessary — prefer editing existing ones
- Keep changes minimal and focused on the task at hand
- Do not add unnecessary comments, docstrings, or type annotations to unchanged code
- Avoid over-engineering; solve for what is asked, not hypothetical future needs
- Do not commit files containing secrets (`.env`, credentials, API keys)
- Always prefix custom fields with `custom_` per ERPNext v16 convention
- Never use `frappe.db.commit()` in doc_events, scheduled jobs, or controllers
- Use `flags.ignore_permissions = True` when creating docs programmatically from hooks
- Run `bench migrate` after modifying DocType JSON files
- Run tests with `bench --site SITE run-tests --app nelito_finance` before committing
