import frappe
from frappe.model.document import Document


class ORFItem(Document):
    def validate(self):
        self.amount = (self.qty or 0) * (self.rate or 0)
        self.validate_milestone_split()

    def validate_milestone_split(self):
        """Ensure milestone split percentages sum to 100 if provided."""
        if not self.milestone_split:
            return

        try:
            parts = [float(p.strip()) for p in self.milestone_split.split(",")]
        except ValueError:
            frappe.throw("Milestone Split must be comma-separated numbers (e.g., 30,15,20,15,20)")

        total = sum(parts)
        if abs(total - 100) > 0.01:
            frappe.throw(
                f"Milestone Split percentages must sum to 100. Current sum: {total}"
            )
