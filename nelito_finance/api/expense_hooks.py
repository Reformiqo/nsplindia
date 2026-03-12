import frappe
from frappe import _

from nelito_finance.api.utils import get_customer_for_project


def on_expense_claim_submit(doc, method):
    """If marked billable to client, auto-create a Sales Invoice."""
    if not doc.custom_billable_to_client:
        return

    if not doc.project:
        frappe.throw(_("Project is required for billable expense claims"))

    project = frappe.get_doc("Project", doc.project)
    customer = get_customer_for_project(project)
    if not customer:
        frappe.throw(
            _("Cannot create invoice: no customer linked to project {0}").format(doc.project)
        )

    si = frappe.new_doc("Sales Invoice")
    si.customer = customer
    si.custom_transaction_origin = "Ad-hoc"
    si.custom_master_contract_id = project.custom_master_contract_id or ""

    for expense in doc.expenses:
        si.append("items", {
            "item_code": "SVC-TRAVEL",
            "item_name": expense.expense_type,
            "description": f"Expense reimbursement: {expense.description or expense.expense_type}",
            "qty": 1,
            "rate": expense.sanctioned_amount or expense.amount,
        })

    si.flags.ignore_permissions = True
    si.flags.ignore_mandatory = True
    si.insert()

    doc.custom_linked_sales_invoice = si.name
    doc.db_set("custom_linked_sales_invoice", si.name, update_modified=False)

    frappe.msgprint(
        _("Sales Invoice {0} created for billable expenses").format(
            frappe.utils.get_link_to_form("Sales Invoice", si.name)
        ),
        alert=True,
    )


