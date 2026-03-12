import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_install():
    """Create all 23 custom fields required by Nelito Finance."""
    create_custom_fields(get_custom_fields(), update=True)
    frappe.db.commit()
    frappe.msgprint("Nelito Finance: Custom fields created successfully.")


def get_custom_fields():
    """Return dict of DocType → list of custom field definitions (23 total)."""
    return {
        # ── Project (7 fields) ──────────────────────────────────────────
        "Project": [
            {
                "fieldname": "custom_master_contract_id",
                "label": "Master Contract ID",
                "fieldtype": "Data",
                "insert_after": "project_name",
                "description": "Root PID grouping e.g., PID_2627_0001",
                "module": "Nelito Finance",
            },
            {
                "fieldname": "custom_parent_project",
                "label": "Parent Project",
                "fieldtype": "Link",
                "options": "Project",
                "insert_after": "custom_master_contract_id",
                "description": "Links sub-PID to parent project",
                "module": "Nelito Finance",
            },
            {
                "fieldname": "custom_revenue_category",
                "label": "Revenue Category",
                "fieldtype": "Select",
                "options": "\nLicense\nImplementation\nAMC\nT&M\nRecurring\nTravel\nOther",
                "insert_after": "custom_parent_project",
                "module": "Nelito Finance",
            },
            {
                "fieldname": "custom_line_value",
                "label": "Line Value",
                "fieldtype": "Currency",
                "insert_after": "custom_revenue_category",
                "description": "Contract value for this PID line",
                "module": "Nelito Finance",
            },
            {
                "fieldname": "custom_total_contract_value",
                "label": "Total Contract Value",
                "fieldtype": "Currency",
                "insert_after": "custom_line_value",
                "read_only": 1,
                "description": "Auto-sum of all child project line values",
                "module": "Nelito Finance",
            },
            {
                "fieldname": "custom_warranty_start",
                "label": "Warranty Start",
                "fieldtype": "Date",
                "insert_after": "custom_total_contract_value",
                "module": "Nelito Finance",
            },
            {
                "fieldname": "custom_warranty_end",
                "label": "Warranty End",
                "fieldtype": "Date",
                "insert_after": "custom_warranty_start",
                "module": "Nelito Finance",
            },
        ],
        # ── Task (5 fields) ─────────────────────────────────────────────
        "Task": [
            {
                "fieldname": "custom_billing_percentage",
                "label": "Billing Percentage",
                "fieldtype": "Percent",
                "insert_after": "project",
                "description": "e.g., 30, 15, 20",
                "module": "Nelito Finance",
            },
            {
                "fieldname": "custom_billing_amount",
                "label": "Billing Amount",
                "fieldtype": "Currency",
                "insert_after": "custom_billing_percentage",
                "read_only": 1,
                "description": "line_value × billing_%",
                "module": "Nelito Finance",
            },
            {
                "fieldname": "custom_billing_status",
                "label": "Billing Status",
                "fieldtype": "Select",
                "options": "\nNot Yet Due\nChargeable\nPartially Invoiced\nFully Invoiced\nOn Hold",
                "insert_after": "custom_billing_amount",
                "default": "Not Yet Due",
                "module": "Nelito Finance",
            },
            {
                "fieldname": "custom_phase",
                "label": "Phase",
                "fieldtype": "Select",
                "options": "\nPhase 1\nPhase 2\nPhase 3\nN/A",
                "insert_after": "custom_billing_status",
                "module": "Nelito Finance",
            },
            {
                "fieldname": "custom_linked_invoice",
                "label": "Linked Invoice",
                "fieldtype": "Link",
                "options": "Sales Invoice",
                "insert_after": "custom_phase",
                "read_only": 1,
                "module": "Nelito Finance",
            },
        ],
        # ── Sales Invoice (4 fields) ────────────────────────────────────
        "Sales Invoice": [
            {
                "fieldname": "custom_transaction_origin",
                "label": "Transaction Origin",
                "fieldtype": "Select",
                "options": "\nMilestone\nTime & Material\nRecurring\nAd-hoc\nCredit Note",
                "insert_after": "naming_series",
                "module": "Nelito Finance",
            },
            {
                "fieldname": "custom_master_contract_id",
                "label": "Master Contract ID",
                "fieldtype": "Data",
                "insert_after": "custom_transaction_origin",
                "module": "Nelito Finance",
            },
            {
                "fieldname": "custom_linked_milestone_task",
                "label": "Linked Milestone Task",
                "fieldtype": "Link",
                "options": "Task",
                "insert_after": "custom_master_contract_id",
                "read_only": 1,
                "module": "Nelito Finance",
            },
            {
                "fieldname": "custom_service_period_from",
                "label": "Service Period From",
                "fieldtype": "Date",
                "insert_after": "custom_linked_milestone_task",
                "module": "Nelito Finance",
            },
        ],
        # ── Sales Order Item (3 fields) ─────────────────────────────────
        "Sales Order Item": [
            {
                "fieldname": "custom_revenue_category",
                "label": "Revenue Category",
                "fieldtype": "Select",
                "options": "\nLicense\nImplementation\nAMC\nT&M\nRecurring\nTravel\nOther",
                "insert_after": "item_code",
                "module": "Nelito Finance",
            },
            {
                "fieldname": "custom_linked_project",
                "label": "Linked Project",
                "fieldtype": "Link",
                "options": "Project",
                "insert_after": "custom_revenue_category",
                "module": "Nelito Finance",
            },
            {
                "fieldname": "custom_line_value",
                "label": "Line Value",
                "fieldtype": "Currency",
                "insert_after": "custom_linked_project",
                "module": "Nelito Finance",
            },
        ],
        # ── Customer (1 field) ──────────────────────────────────────────
        "Customer": [
            {
                "fieldname": "custom_master_contract_ids",
                "label": "Master Contract IDs",
                "fieldtype": "Small Text",
                "insert_after": "customer_name",
                "description": "Comma-separated list of active contract IDs",
                "module": "Nelito Finance",
            },
        ],
        # ── Sales Order (1 field) ───────────────────────────────────────
        "Sales Order": [
            {
                "fieldname": "custom_master_contract_id",
                "label": "Master Contract ID",
                "fieldtype": "Data",
                "insert_after": "naming_series",
                "module": "Nelito Finance",
            },
        ],
        # ── Expense Claim (2 fields) ────────────────────────────────────
        "Expense Claim": [
            {
                "fieldname": "custom_billable_to_client",
                "label": "Billable to Client",
                "fieldtype": "Check",
                "insert_after": "project",
                "description": "If checked, a Sales Invoice will be auto-created on submission",
                "module": "Nelito Finance",
            },
            {
                "fieldname": "custom_linked_sales_invoice",
                "label": "Linked Sales Invoice",
                "fieldtype": "Link",
                "options": "Sales Invoice",
                "insert_after": "custom_billable_to_client",
                "read_only": 1,
                "module": "Nelito Finance",
            },
        ],
    }
