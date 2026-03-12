import frappe
from frappe import _

MAX_PROJECT_DEPTH = 10

REVENUE_CATEGORY_ITEM_MAP = {
    "License": "SVC-LICENSE",
    "Implementation": "SVC-IMPLEMENTATION",
    "AMC": "SVC-AMC",
    "T&M": "SVC-TM",
    "Recurring": "SVC-RECURRING",
    "Travel": "SVC-TRAVEL",
    "Other": "SVC-OTHER",
}


def get_service_item(revenue_category):
    """Map revenue category to standard service item code.

    Args:
        revenue_category: One of License, Implementation, AMC, T&M, Recurring, Travel, Other

    Returns:
        Service item code string (e.g. SVC-LICENSE)
    """
    return REVENUE_CATEGORY_ITEM_MAP.get(revenue_category, "SVC-OTHER")


def get_customer_for_project(project, _depth=0):
    """Resolve customer for a project via Sales Order linkage.

    Walks up the parent project chain until a linked Sales Order is found.

    Args:
        project: Project doc or name
        _depth: Internal recursion counter (do not pass manually)

    Returns:
        Customer name string, or None
    """
    if _depth > MAX_PROJECT_DEPTH:
        frappe.log_error(
            message=f"Max depth exceeded resolving customer for project {project.name}",
            title="Customer Lookup Error",
        )
        return None

    if isinstance(project, str):
        project = frappe.get_doc("Project", project)

    so = frappe.db.get_value(
        "Sales Order Item",
        {"custom_linked_project": project.name},
        "parent",
    )
    if so:
        return frappe.db.get_value("Sales Order", so, "customer")

    if project.custom_parent_project:
        return get_customer_for_project(project.custom_parent_project, _depth + 1)

    return None


@frappe.whitelist()
def get_sub_projects(master_contract_id):
    """Return all sub-projects under a master contract ID.

    Args:
        master_contract_id: The root PID (e.g., PID_2627_0001)

    Returns:
        List of project dicts with name, revenue_category, line_value, status
    """
    return frappe.get_all(
        "Project",
        filters={"custom_master_contract_id": master_contract_id},
        fields=[
            "name", "project_name", "status",
            "custom_revenue_category", "custom_line_value",
            "custom_parent_project", "custom_total_contract_value",
            "custom_warranty_start", "custom_warranty_end",
        ],
        order_by="creation asc",
    )


@frappe.whitelist()
def get_milestone_summary(project):
    """Return milestone task summary for a project.

    Args:
        project: Project name (sub-PID)

    Returns:
        Dict with tasks list, total_billed, total_pending, completion_pct
    """
    tasks = frappe.get_all(
        "Task",
        filters={"project": project, "custom_billing_percentage": [">", 0]},
        fields=[
            "name", "subject", "status",
            "custom_billing_percentage", "custom_billing_amount",
            "custom_billing_status", "custom_phase",
            "custom_linked_invoice",
        ],
        order_by="creation asc",
    )

    total_billed = sum(
        t.custom_billing_amount for t in tasks
        if t.custom_billing_status in ("Partially Invoiced", "Fully Invoiced")
    )
    total_pending = sum(
        t.custom_billing_amount for t in tasks
        if t.custom_billing_status not in ("Partially Invoiced", "Fully Invoiced")
    )
    completed = sum(1 for t in tasks if t.status == "Completed")

    return {
        "tasks": tasks,
        "total_billed": total_billed,
        "total_pending": total_pending,
        "completion_pct": (completed / len(tasks) * 100) if tasks else 0,
    }


@frappe.whitelist()
def get_contract_summary(master_contract_id):
    """Return full contract summary: parent project, sub-projects, and milestone stats.

    Args:
        master_contract_id: The root PID (e.g., PID_2627_0001)

    Returns:
        Dict with parent_project, sub_projects, total_value, total_billed, total_pending
    """
    sub_projects = get_sub_projects(master_contract_id)

    parent = None
    children = []
    for p in sub_projects:
        if not p.custom_parent_project:
            parent = p
        else:
            children.append(p)

    total_value = sum(c.get("custom_line_value", 0) or 0 for c in children)

    # Aggregate billing across all milestone tasks
    total_billed = 0
    total_pending = 0
    for child in children:
        summary = get_milestone_summary(child.name)
        total_billed += summary["total_billed"]
        total_pending += summary["total_pending"]

    return {
        "parent_project": parent,
        "sub_projects": children,
        "total_value": total_value,
        "total_billed": total_billed,
        "total_pending": total_pending,
    }
