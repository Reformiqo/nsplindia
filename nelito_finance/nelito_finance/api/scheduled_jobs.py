import frappe
from frappe import _
from frappe.utils import today, add_years, getdate


def daily_billing_sync():
    """Daily job: recalculate billing amounts for all active milestone tasks.

    Ensures billing_amount stays in sync if project line_value changes.
    """
    tasks = frappe.get_all(
        "Task",
        filters={
            "status": ["not in", ["Completed", "Cancelled"]],
            "custom_billing_percentage": [">", 0],
        },
        fields=["name", "project", "custom_billing_percentage"],
    )

    for task_data in tasks:
        if not task_data.project:
            continue

        line_value = frappe.db.get_value("Project", task_data.project, "custom_line_value") or 0
        new_amount = line_value * (task_data.custom_billing_percentage / 100)

        frappe.db.set_value("Task", task_data.name, "custom_billing_amount", new_amount,
                           update_modified=False)

    frappe.logger().info(f"Daily billing sync: updated {len(tasks)} tasks")


def yearly_amc_renewal():
    """Yearly job: auto-create renewal projects for AMC contracts approaching expiry.

    Looks for AMC sub-projects where warranty_end is within the next 30 days
    and creates a new AMC project for the next year.
    """
    threshold_date = frappe.utils.add_days(today(), 30)

    expiring_projects = frappe.get_all(
        "Project",
        filters={
            "custom_revenue_category": "AMC",
            "custom_warranty_end": ["between", [today(), threshold_date]],
            "status": ["not in", ["Completed", "Cancelled"]],
        },
        fields=["name", "custom_master_contract_id", "custom_parent_project",
                "custom_line_value", "custom_warranty_end", "company"],
    )

    for proj in expiring_projects:
        # Check if renewal already exists
        existing = frappe.db.exists("Project", {
            "custom_parent_project": proj.custom_parent_project,
            "custom_revenue_category": "AMC",
            "custom_warranty_start": proj.custom_warranty_end,
        })
        if existing:
            continue

        new_start = proj.custom_warranty_end
        new_end = add_years(getdate(new_start), 1)

        renewal = frappe.new_doc("Project")
        renewal.project_name = f"{proj.name}-RENEWAL-{getdate(new_start).year}"
        renewal.company = proj.company
        renewal.custom_master_contract_id = proj.custom_master_contract_id
        renewal.custom_parent_project = proj.custom_parent_project
        renewal.custom_revenue_category = "AMC"
        renewal.custom_line_value = proj.custom_line_value
        renewal.custom_warranty_start = new_start
        renewal.custom_warranty_end = new_end

        renewal.flags.ignore_permissions = True
        renewal.insert()

        frappe.logger().info(f"AMC renewal project created: {renewal.name}")
