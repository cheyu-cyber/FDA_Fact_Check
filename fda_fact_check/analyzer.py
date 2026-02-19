"""Analyzer that uses OpenFDA data to fact-check adverse event claims."""

from .openfda_client import OpenFDAClient


class AdverseEventAnalyzer:
    """High-level fact-checking around drug adverse events."""

    def __init__(self, client=None):
        self.client = client or OpenFDAClient()

    def check_drug_reaction(self, drug_name, reaction):
        """Fact-check whether *drug_name* is associated with *reaction*.

        Gathers counts from OpenFDA and returns a summary dict with:
        - ``drug``: the queried drug name
        - ``reaction``: the queried reaction
        - ``drug_total_reports``: total AE reports mentioning the drug
        - ``drug_reaction_reports``: reports mentioning both drug + reaction
        - ``reaction_all_drugs_reports``: reports for the reaction across all drugs
        - ``drug_reaction_proportion``: proportion of the drug's reports
          that mention this reaction
        - ``reaction_drug_proportion``: proportion of all reports for this
          reaction that involve this drug
        - ``summary``: human-readable summary string
        """
        drug_total = self.client.count_adverse_events(drug_name)
        drug_reaction = self.client.count_events_with_reaction(drug_name, reaction)
        reaction_all = self.client.count_reaction_all_drugs(reaction)

        drug_reaction_pct = (
            (drug_reaction / drug_total * 100) if drug_total > 0 else 0.0
        )
        reaction_drug_pct = (
            (drug_reaction / reaction_all * 100) if reaction_all > 0 else 0.0
        )

        summary = self._build_summary(
            drug_name, reaction, drug_total, drug_reaction,
            reaction_all, drug_reaction_pct, reaction_drug_pct,
        )

        return {
            "drug": drug_name,
            "reaction": reaction,
            "drug_total_reports": drug_total,
            "drug_reaction_reports": drug_reaction,
            "reaction_all_drugs_reports": reaction_all,
            "drug_reaction_proportion": round(drug_reaction_pct, 4),
            "reaction_drug_proportion": round(reaction_drug_pct, 4),
            "summary": summary,
        }

    def get_top_reactions_for_drug(self, drug_name, top_n=10):
        """Return the most-commonly reported reactions for a drug."""
        return self.client.get_top_reactions(drug_name, top_n=top_n)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_summary(
        drug, reaction, drug_total, drug_reaction,
        reaction_all, drug_pct, reaction_pct,
    ):
        lines = []
        lines.append(f'Fact-check: Does "{drug}" increase "{reaction}" risk?')
        lines.append("")

        if drug_total == 0:
            lines.append(
                f"No adverse event reports were found for {drug} in the "
                "FDA database."
            )
            return "\n".join(lines)

        lines.append(f"Total adverse event reports for {drug}: {drug_total:,}")
        lines.append(
            f"Reports mentioning both {drug} and {reaction}: "
            f"{drug_reaction:,}"
        )
        lines.append(
            f"Proportion of {drug} reports mentioning {reaction}: "
            f"{drug_pct:.4f}%"
        )

        if reaction_all > 0:
            lines.append(
                f"Total reports for {reaction} across all drugs: "
                f"{reaction_all:,}"
            )
            lines.append(
                f"Proportion of all {reaction} reports involving {drug}: "
                f"{reaction_pct:.4f}%"
            )

        lines.append("")
        if drug_reaction == 0:
            lines.append(
                f"No reports link {drug} to {reaction} in the FDA adverse "
                "event database."
            )
        else:
            lines.append(
                "NOTE: The existence of adverse event reports does NOT prove "
                "causation. These reports are voluntarily submitted and may "
                "contain incomplete or unverified information. A medical "
                "professional should be consulted for clinical guidance."
            )

        return "\n".join(lines)
