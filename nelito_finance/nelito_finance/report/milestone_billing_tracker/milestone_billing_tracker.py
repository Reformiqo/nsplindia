import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "project",
            "label": _("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "width": 200,
        },
        {
            "fieldname": "master_contract_id",
            "label": _("Master Contract ID"),
            "fieldtype": "Data",
            "width": 160,
        },
        {
            "fieldname": "task",
            "label": _("Task"),
            "fieldtype": "Link",
            "options": "Task",
            "width": 200,
        },
        {
            "fieldname": "subject",
            "label": _("Milestone"),
            "fieldtype": "Data",
            "width": 250,
        },
        {
            "fieldname": "phase",
            "label": _("Phase"),
            "fieldtype": "Data",
            "width": 80,
        },
        {
            "fieldname": "billing_percentage",
            "label": _("Billing %"),
            "fieldtype": "Percent",
            "width": 90,
        },
        {
            "fieldname": "billing_amount",
            "label": _("Billing Amount"),
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "fieldname": "billing_status",
            "label": _("Billing Status"),
            "fieldtype": "Data",
            "width": 130,
        },
        {
            "fieldname": "task_status",
            "label": _("Task Status"),
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "fieldname": "linked_invoice",
            "label": _("Invoice"),
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 150,
        },
    ]


def get_data(filters):
    conditions = ""
    values = {}

    if filters and filters.get("project"):
        conditions += " AND t.project = %(project)s"
        values["project"] = filters["project"]

    if filters and filters.get("master_contract_id"):
        conditions += " AND p.custom_master_contract_id = %(master_contract_id)s"
        values["master_contract_id"] = filters["master_contract_id"]

    if filters and filters.get("billing_status"):
        conditions += " AND t.custom_billing_status = %(billing_status)s"
        values["billing_status"] = filters["billing_status"]

    return frappe.db.sql(
        f"""
        SELECT
            t.project,
            p.custom_master_contract_id AS master_contract_id,
            t.name AS task,
            t.subject,
            t.custom_phase AS phase,
            t.custom_billing_percentage AS billing_percentage,
            t.custom_billing_amount AS billing_amount,
            t.custom_billing_status AS billing_status,
            t.status AS task_status,
            t.custom_linked_invoice AS linked_invoice
        FROM `tabTask` t
        LEFT JOIN `tabProject` p ON t.project = p.name
        WHERE t.custom_billing_percentage > 0
            {conditions}
        ORDER BY p.custom_master_contract_id, t.project, t.creation ASC
        """,
        values,
        as_dict=True,
    )
