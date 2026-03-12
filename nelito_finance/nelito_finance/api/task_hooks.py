import frappe
from frappe import _


def on_task_validate(doc, method):
    """Recalculate billing amount from project line_value × billing_%."""
    if not doc.project or not doc.custom_billing_percentage:
        return

    line_value = frappe.db.get_value("Project", doc.project, "custom_line_value") or 0
    doc.custom_billing_amount = line_value * (doc.custom_billing_percentage / 100)


def on_task_update(doc, method):
    """When a task is marked Completed and billing status is Chargeable, trigger invoice logic."""
    if doc.status == "Completed" and doc.custom_billing_status == "Chargeable":
        create_milestone_invoice(doc)

    # Update warranty dates if applicable
    update_warranty_on_completion(doc)


def create_milestone_invoice(task):
    """Create a Sales Invoice for a completed milestone task."""
    project = frappe.get_doc("Project", task.project)
    if not project.custom_master_contract_id:
        return

    # Get customer from project or sales order
    customer = get_customer_for_project(project)
    if not customer:
        frappe.log_error(
            f"Cannot create invoice for task {task.name}: no customer found",
            "Milestone Invoice Error",
        )
        return

    si = frappe.new_doc("Sales Invoice")
    si.customer = customer
    si.custom_transaction_origin = "Milestone"
    si.custom_master_contract_id = project.custom_master_contract_id
    si.custom_linked_milestone_task = task.name

    item_code = _get_service_item(project.custom_revenue_category)
    si.append("items", {
        "item_code": item_code,
        "item_name": task.subject,
        "description": f"Milestone billing: {task.subject}",
        "qty": 1,
        "rate": task.custom_billing_amount or 0,
    })

    si.flags.ignore_permissions = True
    si.flags.ignore_mandatory = True
    si.insert()

    # Link the invoice back to the task
    task.db_set("custom_linked_invoice", si.name)
    task.db_set("custom_billing_status", "Fully Invoiced")

    frappe.msgprint(
        _("Sales Invoice {0} created for milestone: {1}").format(
            frappe.utils.get_link_to_form("Sales Invoice", si.name),
            task.subject,
        ),
        alert=True,
    )


def update_warranty_on_completion(task):
    """If all milestones of a project are completed, set warranty dates."""
    if task.status != "Completed" or not task.project:
        return

    project = frappe.get_doc("Project", task.project)
    if project.custom_revenue_category != "Implementation":
        return

    # Check if all tasks in this project are completed
    incomplete = frappe.db.count("Task", {
        "project": task.project,
        "status": ["not in", ["Completed", "Cancelled"]],
    })

    if incomplete == 0 and not project.custom_warranty_start:
        today = frappe.utils.today()
        project.db_set("custom_warranty_start", today)
        project.db_set("custom_warranty_end", frappe.utils.add_months(today, 12))


def get_customer_for_project(project):
    """Resolve customer for a project via Sales Order linkage."""
    # Check if project has a linked Sales Order
    so = frappe.db.get_value(
        "Sales Order Item",
        {"custom_linked_project": project.name},
        "parent",
    )
    if so:
        return frappe.db.get_value("Sales Order", so, "customer")

    # Fallback: check parent project
    if project.custom_parent_project:
        parent = frappe.get_doc("Project", project.custom_parent_project)
        return get_customer_for_project(parent)

    return None


def _get_service_item(revenue_category):
    """Map revenue category to service item code."""
    mapping = {
        "License": "SVC-LICENSE",
        "Implementation": "SVC-IMPLEMENTATION",
        "AMC": "SVC-AMC",
        "T&M": "SVC-TM",
        "Recurring": "SVC-RECURRING",
        "Travel": "SVC-TRAVEL",
        "Other": "SVC-OTHER",
    }
    return mapping.get(revenue_category, "SVC-OTHER")
