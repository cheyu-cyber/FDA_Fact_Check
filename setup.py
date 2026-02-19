from setuptools import setup, find_packages

setup(
    name="fda_fact_check",
    version="0.1.0",
    description="Adverse event tracking and fact-checking using OpenFDA APIs",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "fda-fact-check=fda_fact_check.cli:main",
        ],
    },
)
