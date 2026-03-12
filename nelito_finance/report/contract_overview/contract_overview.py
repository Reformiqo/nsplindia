import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "master_contract_id",
            "label": _("Master Contract ID"),
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "fieldname": "parent_project",
            "label": _("Parent Project"),
            "fieldtype": "Link",
            "options": "Project",
            "width": 200,
        },
        {
            "fieldname": "sub_project",
            "label": _("Sub Project"),
            "fieldtype": "Link",
            "options": "Project",
            "width": 200,
        },
        {
            "fieldname": "revenue_category",
            "label": _("Revenue Category"),
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "fieldname": "line_value",
            "label": _("Line Value"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "total_contract_value",
            "label": _("Total Contract Value"),
            "fieldtype": "Currency",
            "width": 170,
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "fieldname": "warranty_start",
            "label": _("Warranty Start"),
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "fieldname": "warranty_end",
            "label": _("Warranty End"),
            "fieldtype": "Date",
            "width": 120,
        },
    ]


def get_data(filters):
    conditions = ""
    values = {}

    if filters and filters.get("master_contract_id"):
        conditions += " AND p.custom_master_contract_id = %(master_contract_id)s"
        values["master_contract_id"] = filters["master_contract_id"]

    if filters and filters.get("revenue_category"):
        conditions += " AND p.custom_revenue_category = %(revenue_category)s"
        values["revenue_category"] = filters["revenue_category"]

    # Get parent projects (no parent_project link)
    parents = frappe.db.sql(
        f"""
        SELECT
            p.custom_master_contract_id AS master_contract_id,
            p.name AS parent_project,
            '' AS sub_project,
            '' AS revenue_category,
            0 AS line_value,
            p.custom_total_contract_value AS total_contract_value,
            p.status,
            p.custom_warranty_start AS warranty_start,
            p.custom_warranty_end AS warranty_end
        FROM `tabProject` p
        WHERE p.custom_parent_project IS NULL
            AND p.custom_master_contract_id IS NOT NULL
            AND p.custom_master_contract_id != ''
            {conditions}
        ORDER BY p.creation ASC
        """,
        values,
        as_dict=True,
    )

    data = []
    for parent in parents:
        data.append(parent)

        # Get children for this parent
        children = frappe.db.sql(
            """
            SELECT
                c.custom_master_contract_id AS master_contract_id,
                c.custom_parent_project AS parent_project,
                c.name AS sub_project,
                c.custom_revenue_category AS revenue_category,
                c.custom_line_value AS line_value,
                0 AS total_contract_value,
                c.status,
                c.custom_warranty_start AS warranty_start,
                c.custom_warranty_end AS warranty_end
            FROM `tabProject` c
            WHERE c.custom_parent_project = %s
            ORDER BY c.creation ASC
            """,
            parent.parent_project,
            as_dict=True,
        )
        data.extend(children)

    return data
