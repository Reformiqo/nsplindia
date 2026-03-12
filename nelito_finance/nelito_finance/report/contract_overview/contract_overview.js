frappe.query_reports["Contract Overview"] = {
    filters: [
        {
            fieldname: "master_contract_id",
            label: __("Master Contract ID"),
            fieldtype: "Data",
        },
        {
            fieldname: "revenue_category",
            label: __("Revenue Category"),
            fieldtype: "Select",
            options: "\nLicense\nImplementation\nAMC\nT&M\nRecurring\nTravel\nOther",
        },
    ],
};
