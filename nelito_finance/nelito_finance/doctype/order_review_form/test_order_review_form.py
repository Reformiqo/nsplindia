import frappe
from frappe.tests.utils import FrappeTestCase


class TestOrderReviewForm(FrappeTestCase):
    def setUp(self):
        # Ensure service items exist
        for code in ["SVC-LICENSE", "SVC-IMPLEMENTATION", "SVC-AMC", "SVC-TM", "SVC-TRAVEL"]:
            if not frappe.db.exists("Item", code):
                item = frappe.new_doc("Item")
                item.item_code = code
                item.item_name = code
                item.item_group = "Services"
                item.flags.ignore_permissions = True
                item.insert()

    def test_total_calculation(self):
        """Total contract value should equal sum of line item amounts."""
        orf = frappe.new_doc("Order Review Form")
        orf.customer = "_Test Customer"
        orf.contract_date = frappe.utils.today()
        orf.master_contract_id = "PID_TEST_0001"
        orf.append("items", {
            "revenue_category": "License",
            "item_description": "Test License",
            "qty": 1,
            "rate": 5000000,
        })
        orf.append("items", {
            "revenue_category": "Implementation",
            "item_description": "Test Implementation",
            "qty": 1,
            "rate": 3000000,
        })
        orf.validate()
        self.assertEqual(orf.total_contract_value, 8000000)
        self.assertEqual(orf.number_of_lines, 2)

    def test_milestone_split_validation(self):
        """Milestone split must sum to 100."""
        orf_item = frappe.new_doc("ORF Item")
        orf_item.revenue_category = "Implementation"
        orf_item.item_description = "Test"
        orf_item.qty = 1
        orf_item.rate = 1000000
        orf_item.milestone_split = "30,15,20,15,20"
        orf_item.validate()  # Should pass

        orf_item.milestone_split = "30,15,20"
        self.assertRaises(frappe.ValidationError, orf_item.validate)

    def test_pid_format_generation(self):
        """PID format preview should be generated from master_contract_id."""
        orf = frappe.new_doc("Order Review Form")
        orf.master_contract_id = "PID_2627_0001"
        orf.append("items", {
            "revenue_category": "License",
            "item_description": "Test",
            "qty": 1,
            "rate": 100,
        })
        orf.validate()
        self.assertEqual(orf.pid_format, "PID_2627_0001-00 (parent)")
