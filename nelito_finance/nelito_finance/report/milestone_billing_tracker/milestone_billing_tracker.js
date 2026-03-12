frappe.query_reports["Milestone Billing Tracker"] = {
    filters: [
        {
            fieldname: "project",
            label: __("Project"),
            fieldtype: "Link",
            options: "Project",
        },
        {
            fieldname: "master_contract_id",
            label: __("Master Contract ID"),
            fieldtype: "Data",
        },
        {
            fieldname: "billing_status",
            label: __("Billing Status"),
            fieldtype: "Select",
            options: "\nNot Yet Due\nChargeable\nPartially Invoiced\nFully Invoiced\nOn Hold",
        },
    ],
};
