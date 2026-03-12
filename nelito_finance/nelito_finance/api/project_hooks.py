import frappe
from frappe import _


def on_project_validate(doc, method):
    """Auto-sum child project line values into parent's total_contract_value."""
    if not doc.custom_parent_project:
        # This is a parent project — recalculate total from children
        recalculate_parent_total(doc.name, doc)


def on_project_update(doc, method):
    """When a sub-project's line_value changes, update the parent total."""
    if doc.custom_parent_project:
        update_parent_contract_value(doc.custom_parent_project)


def recalculate_parent_total(project_name, doc=None):
    """Sum all child project line values and set on the parent project."""
    total = frappe.db.sql(
        """
        SELECT COALESCE(SUM(custom_line_value), 0)
        FROM `tabProject`
        WHERE custom_parent_project = %s
        """,
        project_name,
    )[0][0]

    if doc:
        doc.custom_total_contract_value = total
    else:
        frappe.db.set_value("Project", project_name, "custom_total_contract_value", total)


def update_parent_contract_value(parent_project_name):
    """Recalculate and persist the parent project's total contract value."""
    recalculate_parent_total(parent_project_name)
