app_name = "nelito_finance"
app_title = "Nelito Finance"
app_publisher = "Nelito Systems Pvt. Ltd."
app_description = "Revenue Management, Project Accounting & Milestone Billing"
app_email = "info@nelito.com"
app_license = "MIT"

# Apps
required_apps = ["frappe", "erpnext"]

# Each additional app/module to be included in the website
# add_to_apps_screen = [
# 	{
# 		"name": "nelito_finance",
# 		"logo": "/assets/nelito_finance/images/logo.png",
# 		"title": "Nelito Finance",
# 		"route": "/nelito_finance",
# 	}
# ]

# After Install
# ---------------------------------------------------------------------------
after_install = "nelito_finance.install.after_install"

# DocType Events
# ---------------------------------------------------------------------------
doc_events = {
    "Task": {
        "validate": "nelito_finance.api.task_hooks.on_task_validate",
        "on_update": "nelito_finance.api.task_hooks.on_task_update",
    },
    "Project": {
        "validate": "nelito_finance.api.project_hooks.on_project_validate",
        "on_update": "nelito_finance.api.project_hooks.on_project_update",
    },
    "Expense Claim": {
        "on_submit": "nelito_finance.api.expense_hooks.on_expense_claim_submit",
    },
}

# Scheduled Tasks
# ---------------------------------------------------------------------------
scheduler_events = {
    "daily": [
        "nelito_finance.api.scheduled_jobs.daily_billing_sync",
    ],
    "yearly": [
        "nelito_finance.api.scheduled_jobs.yearly_amc_renewal",
    ],
}

# Fixtures
# ---------------------------------------------------------------------------
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "Nelito Finance"]],
    },
]

# App Includes
# ---------------------------------------------------------------------------
app_include_js = "/assets/nelito_finance/js/project_custom.js"

# Override whitelisted methods
# ---------------------------------------------------------------------------
# override_whitelisted_methods = {}

# Override DocType class
# ---------------------------------------------------------------------------
# override_doctype_class = {}

# Jinja Environment Customizations
# ---------------------------------------------------------------------------
# jinja = {}

# Website
# ---------------------------------------------------------------------------
# website_route_rules = []
