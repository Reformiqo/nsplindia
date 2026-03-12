import frappe
from frappe import _
from frappe.model.document import Document


class OrderReviewForm(Document):
    def validate(self):
        self.calculate_totals()
        self.generate_pid_format()

    def calculate_totals(self):
        """Recalculate total contract value and line count from child items."""
        total = 0
        for item in self.items:
            item.amount = (item.qty or 0) * (item.rate or 0)
            total += item.amount
        self.total_contract_value = total
        self.number_of_lines = len(self.items)

    def generate_pid_format(self):
        """Generate preview of PID sub-project naming."""
        if self.master_contract_id:
            self.pid_format = f"{self.master_contract_id}-00 (parent)"

    def on_submit(self):
        """Auto-create Sales Order, Parent Project, Sub-Projects, and Tasks."""
        so = self.create_sales_order()
        parent_project = self.create_parent_project()
        self.create_sub_projects_and_tasks(parent_project)

        # Set on self so the framework persists them in the final save
        self.sales_order = so.name
        self.parent_project = parent_project.name

    def create_sales_order(self):
        """Create a Sales Order from ORF line items."""
        so = frappe.new_doc("Sales Order")
        so.customer = self.customer
        so.delivery_date = frappe.utils.add_days(self.contract_date, 365)
        so.custom_master_contract_id = self.master_contract_id

        for item in self.items:
            so.append("items", {
                "item_code": item.item_code or self.get_service_item(item.revenue_category),
                "item_name": item.item_description,
                "description": item.item_description,
                "qty": item.qty,
                "rate": item.rate,
                "custom_revenue_category": item.revenue_category,
                "custom_line_value": item.amount,
            })

        so.flags.ignore_permissions = True
        so.flags.ignore_mandatory = True
        so.insert()
        so.submit()
        return so

    def create_parent_project(self):
        """Create a parent Project (PID-00) to group all sub-projects."""
        project = frappe.new_doc("Project")
        project.project_name = f"{self.master_contract_id}-00"
        project.company = frappe.defaults.get_defaults().get("company")
        project.custom_master_contract_id = self.master_contract_id
        project.custom_total_contract_value = self.total_contract_value

        project.flags.ignore_permissions = True
        project.insert()
        return project

    def create_sub_projects_and_tasks(self, parent_project):
        """Create one sub-Project per line item, with milestone Tasks if applicable."""
        for idx, item in enumerate(self.items, start=1):
            sub_pid = f"{self.master_contract_id}-{idx:02d}"
            project = frappe.new_doc("Project")
            project.project_name = sub_pid
            project.company = frappe.defaults.get_defaults().get("company")
            project.custom_master_contract_id = self.master_contract_id
            project.custom_parent_project = parent_project.name
            project.custom_revenue_category = item.revenue_category
            project.custom_line_value = item.amount

            project.flags.ignore_permissions = True
            project.insert()

            # Create milestone tasks if milestone_split is defined
            if item.milestone_split:
                self.create_milestone_tasks(project, item)

    def create_milestone_tasks(self, project, item):
        """Create Task records based on milestone split percentages."""
        percentages = [float(p.strip()) for p in item.milestone_split.split(",")]
        for i, pct in enumerate(percentages, start=1):
            task = frappe.new_doc("Task")
            task.subject = f"{item.item_description} - Milestone {i}"
            task.project = project.name
            task.custom_billing_percentage = pct
            task.custom_billing_amount = (item.amount or 0) * pct / 100
            task.custom_billing_status = "Not Yet Due"
            task.custom_phase = f"Phase {min(i, 3)}" if i <= 3 else "N/A"

            task.flags.ignore_permissions = True
            task.insert()

    @staticmethod
    def get_service_item(revenue_category):
        """Map revenue category to standard service item code."""
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
