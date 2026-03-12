frappe.ui.form.on("Order Review Form", {
    refresh: function (frm) {
        // Show view buttons for linked documents after submission
        if (frm.doc.docstatus === 1) {
            if (frm.doc.sales_order) {
                frm.add_custom_button(__("View Sales Order"), function () {
                    frappe.set_route("Form", "Sales Order", frm.doc.sales_order);
                }, __("View"));
            }
            if (frm.doc.parent_project) {
                frm.add_custom_button(__("View Parent Project"), function () {
                    frappe.set_route("Form", "Project", frm.doc.parent_project);
                }, __("View"));
            }
        }
    },

    validate: function (frm) {
        frm.trigger("calculate_totals");
    },

    calculate_totals: function (frm) {
        let total = 0;
        (frm.doc.items || []).forEach(function (row) {
            row.amount = (row.qty || 0) * (row.rate || 0);
            total += row.amount;
        });
        frm.set_value("total_contract_value", total);
        frm.set_value("number_of_lines", (frm.doc.items || []).length);
        frm.refresh_fields();
    },
});

frappe.ui.form.on("ORF Item", {
    qty: function (frm) {
        frm.trigger("calculate_totals");
    },
    rate: function (frm) {
        frm.trigger("calculate_totals");
    },
    items_remove: function (frm) {
        frm.trigger("calculate_totals");
    },
});
