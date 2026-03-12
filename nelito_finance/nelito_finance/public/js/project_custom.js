// Nelito Finance — Task & Project form customizations
// v16 compatible: no bare global functions (JS loaded as IIFEs)

frappe.provide("frappe.nelito_finance");

// Task: "Create Invoice" button and billing field toggle
frappe.ui.form.on("Task", {
    refresh: function (frm) {
        // Show "Create Invoice" button for chargeable milestones
        if (
            frm.doc.custom_billing_status === "Chargeable" &&
            frm.doc.status === "Completed" &&
            !frm.doc.custom_linked_invoice
        ) {
            frm.add_custom_button(__("Create Invoice"), function () {
                frappe.confirm(
                    __(
                        "Create a Sales Invoice for milestone: {0} (₹{1})?",
                        [frm.doc.subject, frm.doc.custom_billing_amount]
                    ),
                    function () {
                        // Trigger invoice creation by setting billing status
                        frm.set_value("custom_billing_status", "Chargeable");
                        frm.save();
                    }
                );
            }, __("Actions"));
        }

        // Toggle billing fields visibility based on billing percentage
        frm.toggle_display(
            ["custom_billing_amount", "custom_billing_status", "custom_phase", "custom_linked_invoice"],
            frm.doc.custom_billing_percentage > 0
        );
    },

    custom_billing_percentage: function (frm) {
        // Recalculate billing amount when percentage changes
        if (frm.doc.project && frm.doc.custom_billing_percentage) {
            frappe.db.get_value(
                "Project",
                frm.doc.project,
                "custom_line_value",
                function (r) {
                    if (r && r.custom_line_value) {
                        frm.set_value(
                            "custom_billing_amount",
                            r.custom_line_value * (frm.doc.custom_billing_percentage / 100)
                        );
                    }
                }
            );
        }
    },
});

// Project: Sub-PID dashboard
frappe.ui.form.on("Project", {
    refresh: function (frm) {
        // Show sub-projects dashboard for parent projects
        if (frm.doc.custom_master_contract_id && !frm.doc.custom_parent_project) {
            frm.add_custom_button(__("View Sub-Projects"), function () {
                frappe.set_route("List", "Project", {
                    custom_parent_project: frm.doc.name,
                });
            });

            frm.add_custom_button(__("Contract Summary"), function () {
                frappe.call({
                    method: "nelito_finance.api.utils.get_contract_summary",
                    args: { master_contract_id: frm.doc.custom_master_contract_id },
                    callback: function (r) {
                        if (r.message) {
                            frappe.nelito_finance.show_contract_summary(r.message);
                        }
                    },
                });
            });
        }

        // Show milestone summary for sub-projects with milestones
        if (frm.doc.custom_parent_project) {
            frm.add_custom_button(__("Milestone Summary"), function () {
                frappe.call({
                    method: "nelito_finance.api.utils.get_milestone_summary",
                    args: { project: frm.doc.name },
                    callback: function (r) {
                        if (r.message) {
                            frappe.nelito_finance.show_milestone_summary(frm.doc.name, r.message);
                        }
                    },
                });
            });
        }
    },
});

frappe.nelito_finance.show_contract_summary = function (summary) {
    let rows = "";
    (summary.sub_projects || []).forEach(function (p) {
        rows += "<tr>"
            + "<td>" + p.name + "</td>"
            + "<td>" + (p.custom_revenue_category || "") + "</td>"
            + "<td class='text-right'>" + frappe.format(p.custom_line_value || 0, { fieldtype: "Currency" }) + "</td>"
            + "<td>" + (p.status || "") + "</td>"
            + "</tr>";
    });

    let html = "<div class='frappe-card'>"
        + "<table class='table table-bordered'>"
        + "<thead><tr>"
        + "<th>" + __("Sub-Project") + "</th>"
        + "<th>" + __("Category") + "</th>"
        + "<th class='text-right'>" + __("Line Value") + "</th>"
        + "<th>" + __("Status") + "</th>"
        + "</tr></thead>"
        + "<tbody>" + rows + "</tbody>"
        + "<tfoot><tr>"
        + "<td colspan='2'><strong>" + __("Total") + "</strong></td>"
        + "<td class='text-right'><strong>" + frappe.format(summary.total_value || 0, { fieldtype: "Currency" }) + "</strong></td>"
        + "<td></td>"
        + "</tr><tr>"
        + "<td colspan='2'>" + __("Billed") + "</td>"
        + "<td class='text-right'>" + frappe.format(summary.total_billed || 0, { fieldtype: "Currency" }) + "</td>"
        + "<td></td>"
        + "</tr><tr>"
        + "<td colspan='2'>" + __("Pending") + "</td>"
        + "<td class='text-right'>" + frappe.format(summary.total_pending || 0, { fieldtype: "Currency" }) + "</td>"
        + "<td></td>"
        + "</tr></tfoot>"
        + "</table></div>";

    frappe.msgprint({ title: __("Contract Summary"), message: html, wide: true });
};

frappe.nelito_finance.show_milestone_summary = function (project_name, summary) {
    let rows = "";
    (summary.tasks || []).forEach(function (t) {
        rows += "<tr>"
            + "<td>" + t.subject + "</td>"
            + "<td>" + (t.custom_phase || "") + "</td>"
            + "<td class='text-right'>" + (t.custom_billing_percentage || 0) + "%</td>"
            + "<td class='text-right'>" + frappe.format(t.custom_billing_amount || 0, { fieldtype: "Currency" }) + "</td>"
            + "<td>" + (t.custom_billing_status || "") + "</td>"
            + "<td>" + (t.status || "") + "</td>"
            + "</tr>";
    });

    let html = "<div class='frappe-card'>"
        + "<p><strong>" + __("Completion") + ":</strong> " + (summary.completion_pct || 0).toFixed(1) + "%</p>"
        + "<table class='table table-bordered'>"
        + "<thead><tr>"
        + "<th>" + __("Milestone") + "</th>"
        + "<th>" + __("Phase") + "</th>"
        + "<th class='text-right'>" + __("Billing %") + "</th>"
        + "<th class='text-right'>" + __("Amount") + "</th>"
        + "<th>" + __("Billing Status") + "</th>"
        + "<th>" + __("Task Status") + "</th>"
        + "</tr></thead>"
        + "<tbody>" + rows + "</tbody>"
        + "<tfoot><tr>"
        + "<td colspan='3'><strong>" + __("Billed / Pending") + "</strong></td>"
        + "<td class='text-right'>" + frappe.format(summary.total_billed || 0, { fieldtype: "Currency" })
            + " / " + frappe.format(summary.total_pending || 0, { fieldtype: "Currency" }) + "</td>"
        + "<td colspan='2'></td>"
        + "</tr></tfoot>"
        + "</table></div>";

    frappe.msgprint({ title: __("Milestone Summary — " + project_name), message: html, wide: true });
};
