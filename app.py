"""
FDA Adverse Event Fact Checker
Uses the OpenFDA Drug Event API to fact-check claims about drug-related adverse events.
"""

import requests
from flask import Flask, render_template, request

app = Flask(__name__)

OPENFDA_BASE_URL = "https://api.fda.gov/drug/event.json"
# Number of reports required to consider an association "notable"
NOTABLE_REPORT_THRESHOLD = 50


def query_adverse_events(drug_name: str, reaction: str) -> dict:
    """
    Query the OpenFDA Drug Adverse Event API for reports linking a drug to a reaction.

    Returns a dict with keys:
        total_drug_reports   – total reports mentioning the drug
        reaction_reports     – reports mentioning the drug AND the reaction
        error                – error message string, or None
    """
    result = {"total_drug_reports": 0, "reaction_reports": 0, "error": None}

    drug_filter = f'patient.drug.medicinalproduct:"{drug_name}"'
    reaction_filter = f'patient.reaction.reactionmeddrapt:"{reaction}"'

    try:
        # Total reports for the drug
        resp = requests.get(
            OPENFDA_BASE_URL,
            params={"search": drug_filter, "limit": 1},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        result["total_drug_reports"] = data.get("meta", {}).get("results", {}).get("total", 0)

        # Reports for drug + reaction
        resp2 = requests.get(
            OPENFDA_BASE_URL,
            params={"search": f"{drug_filter} AND {reaction_filter}", "limit": 1},
            timeout=10,
        )
        if resp2.status_code == 404:
            # No results found for this combination
            result["reaction_reports"] = 0
        else:
            resp2.raise_for_status()
            data2 = resp2.json()
            result["reaction_reports"] = (
                data2.get("meta", {}).get("results", {}).get("total", 0)
            )

    except requests.exceptions.Timeout:
        result["error"] = "The OpenFDA API request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        result["error"] = "Could not connect to the OpenFDA API. Please check your internet connection."
    except requests.exceptions.HTTPError as exc:
        result["error"] = f"OpenFDA API returned an error: {exc.response.status_code}"
    except (KeyError, ValueError) as exc:
        result["error"] = f"Unexpected response from OpenFDA API: {exc}"

    return result


def build_verdict(drug_name: str, reaction: str, total: int, reaction_count: int) -> dict:
    """
    Build a human-readable verdict from the raw counts.

    Returns a dict with keys:
        label     – 'SUPPORTED', 'INSUFFICIENT EVIDENCE', or 'NOT SUPPORTED'
        summary   – one-sentence summary
        detail    – longer explanation
    """
    if total == 0:
        return {
            "label": "NOT SUPPORTED",
            "summary": f"No adverse event reports were found for '{drug_name}' in the FDA database.",
            "detail": (
                "The OpenFDA adverse event database contains no reports for this drug. "
                "This may mean the drug name is spelled differently in the database, "
                "or that no reports have been filed."
            ),
        }

    if reaction_count == 0:
        return {
            "label": "NOT SUPPORTED",
            "summary": (
                f"Out of {total:,} FDA adverse event reports for '{drug_name}', "
                f"none mention '{reaction}'."
            ),
            "detail": (
                f"There are {total:,} adverse event reports for '{drug_name}' in the FDA database, "
                f"but none of them mention '{reaction}' as a reported reaction. "
                "This does not constitute scientific proof, but current FDA adverse event data "
                "does not support this claim."
            ),
        }

    pct = (reaction_count / total) * 100

    if reaction_count >= NOTABLE_REPORT_THRESHOLD:
        label = "SUPPORTED"
        summary = (
            f"{reaction_count:,} out of {total:,} FDA adverse event reports "
            f"for '{drug_name}' mention '{reaction}' ({pct:.2f}%)."
        )
        detail = (
            f"The FDA adverse event reporting system (FAERS) contains {reaction_count:,} "
            f"reports associating '{drug_name}' with '{reaction}'. "
            "Note: adverse event reports indicate an association was observed and reported, "
            "but do not prove causation. A healthcare professional should be consulted "
            "for medical decisions."
        )
    else:
        label = "INSUFFICIENT EVIDENCE"
        summary = (
            f"Only {reaction_count:,} out of {total:,} FDA adverse event reports "
            f"for '{drug_name}' mention '{reaction}' ({pct:.2f}%)."
        )
        detail = (
            f"The FDA adverse event reporting system (FAERS) contains {reaction_count:,} "
            f"reports associating '{drug_name}' with '{reaction}', which is below the "
            f"threshold of {NOTABLE_REPORT_THRESHOLD} reports considered notable. "
            "Adverse event reports indicate an association was observed and reported, "
            "but do not prove causation."
        )

    return {"label": label, "summary": summary, "detail": detail}


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    drug_name = ""
    reaction = ""

    if request.method == "POST":
        drug_name = request.form.get("drug_name", "").strip()
        reaction = request.form.get("reaction", "").strip()

        if drug_name and reaction:
            api_result = query_adverse_events(drug_name, reaction)
            if api_result["error"]:
                result = {"error": api_result["error"]}
            else:
                verdict = build_verdict(
                    drug_name,
                    reaction,
                    api_result["total_drug_reports"],
                    api_result["reaction_reports"],
                )
                result = {
                    "drug_name": drug_name,
                    "reaction": reaction,
                    "total_drug_reports": api_result["total_drug_reports"],
                    "reaction_reports": api_result["reaction_reports"],
                    "verdict": verdict,
                }
        else:
            result = {"error": "Please enter both a drug name and a reaction/condition."}

    return render_template("index.html", result=result, drug_name=drug_name, reaction=reaction)


if __name__ == "__main__":
    import os
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")
