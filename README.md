# FDA Fact Check

Adverse event tracking and fact-checking tool powered by the [OpenFDA API](https://open.fda.gov/apis/drug/event/).

Query FDA adverse event reports to investigate claims like *"Does Tylenol increase autism risk?"* and get data-driven context straight from the FAERS database.

## Installation

```bash
pip install -e .
```

## Usage

### Check a specific drug + reaction claim

```bash
fda-fact-check Tylenol autism
```

Example output:

```
Fact-check: Does "Tylenol" increase "autism" risk?

Total adverse event reports for Tylenol: 85,214
Reports mentioning both Tylenol and autism: 12
Proportion of Tylenol reports mentioning autism: 0.0141%
Total reports for autism across all drugs: 1,203
Proportion of all autism reports involving Tylenol: 0.9975%

NOTE: The existence of adverse event reports does NOT prove causation.
These reports are voluntarily submitted and may contain incomplete or
unverified information. A medical professional should be consulted for
clinical guidance.
```

### List top reported reactions for a drug

```bash
fda-fact-check Tylenol
```

### JSON output

```bash
fda-fact-check Tylenol autism --json
```

### Use an API key (optional, increases rate limits)

```bash
fda-fact-check Tylenol autism --api-key YOUR_KEY
```

## Running tests

```bash
pip install pytest
pytest tests/ -v
```

## How it works

1. Queries the OpenFDA drug adverse event endpoint for report counts.
2. Compares the number of reports mentioning both the drug and the reaction against total reports for the drug and total reports for the reaction across all drugs.
3. Computes proportions and returns a fact-check summary with appropriate disclaimers.

> **Disclaimer:** Adverse event reports do not establish causation. FAERS data is voluntarily submitted and may be incomplete. Always consult a healthcare professional.
