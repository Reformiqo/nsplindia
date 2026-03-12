from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="nelito_finance",
    version="0.0.1",
    description="Revenue Management, Project Accounting & Milestone Billing for Nelito Systems",
    author="Nelito Systems Pvt. Ltd.",
    author_email="info@nelito.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
