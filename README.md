# FDA Adverse Event Fact Checker

A web application that fact-checks drug-related adverse event claims using real FDA reporting data from the [OpenFDA Drug Event API](https://open.fda.gov/apis/drug/event/).

## What it does

Enter a **drug name** and an **adverse reaction or condition** to see how many FDA adverse event reports link the two.  
For example: *"Does Tylenol increase autism rates?"* — the app queries the FDA Adverse Event Reporting System (FAERS) and returns a verdict:

| Verdict | Meaning |
|---|---|
| ✅ **SUPPORTED** | 50 or more reports link the drug to the reaction |
| ⚠️ **INSUFFICIENT EVIDENCE** | Reports exist but fall below the notable threshold |
| ❌ **NOT SUPPORTED** | No reports link the drug to the reaction in FAERS |

> **Disclaimer:** Adverse event reports are submitted voluntarily and indicate an association was observed, not that the drug caused the event. Always consult a healthcare professional.

## Project structure

```
FDA_Fact_Check/
├── app.py              # Flask application & OpenFDA API logic
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Jinja2 HTML template
├── static/
│   └── style.css       # Stylesheet
└── tests/
    └── test_app.py     # Unit & integration tests (pytest)
```

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
python app.py
```

Then open <http://127.0.0.1:5000> in your browser.

## Running tests

```bash
pytest tests/ -v
```

## Example queries

- **Tylenol** → Autism  
- **Ibuprofen** → Heart attack  
- **Aspirin** → Gastrointestinal haemorrhage
