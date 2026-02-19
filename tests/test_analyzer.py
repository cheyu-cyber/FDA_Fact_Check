"""Tests for AdverseEventAnalyzer."""

import unittest
from unittest.mock import MagicMock

from fda_fact_check.analyzer import AdverseEventAnalyzer


class TestAdverseEventAnalyzer(unittest.TestCase):

    def _make_analyzer(self, drug_total=1000, drug_reaction=5, reaction_all=200):
        """Return an analyzer with a mock client."""
        client = MagicMock()
        client.count_adverse_events.return_value = drug_total
        client.count_events_with_reaction.return_value = drug_reaction
        client.count_reaction_all_drugs.return_value = reaction_all
        return AdverseEventAnalyzer(client=client)

    # -- check_drug_reaction ------------------------------------------------

    def test_check_drug_reaction_basic(self):
        analyzer = self._make_analyzer(drug_total=1000, drug_reaction=5, reaction_all=200)
        result = analyzer.check_drug_reaction("Tylenol", "autism")

        self.assertEqual(result["drug"], "Tylenol")
        self.assertEqual(result["reaction"], "autism")
        self.assertEqual(result["drug_total_reports"], 1000)
        self.assertEqual(result["drug_reaction_reports"], 5)
        self.assertEqual(result["reaction_all_drugs_reports"], 200)
        self.assertAlmostEqual(result["drug_reaction_proportion"], 0.5, places=2)
        self.assertAlmostEqual(result["reaction_drug_proportion"], 2.5, places=2)
        self.assertIn("Tylenol", result["summary"])
        self.assertIn("autism", result["summary"])

    def test_check_drug_reaction_zero_drug_reports(self):
        analyzer = self._make_analyzer(drug_total=0, drug_reaction=0, reaction_all=100)
        result = analyzer.check_drug_reaction("FakeDrug", "headache")

        self.assertEqual(result["drug_reaction_proportion"], 0.0)
        self.assertIn("No adverse event reports", result["summary"])

    def test_check_drug_reaction_zero_reaction_reports(self):
        analyzer = self._make_analyzer(drug_total=500, drug_reaction=0, reaction_all=0)
        result = analyzer.check_drug_reaction("Aspirin", "telekinesis")

        self.assertEqual(result["drug_reaction_reports"], 0)
        self.assertIn("No reports link", result["summary"])

    def test_summary_includes_causation_disclaimer(self):
        analyzer = self._make_analyzer(drug_total=1000, drug_reaction=10, reaction_all=50)
        result = analyzer.check_drug_reaction("Tylenol", "autism")

        self.assertIn("does NOT prove causation", result["summary"])

    # -- get_top_reactions_for_drug ----------------------------------------

    def test_get_top_reactions_delegates_to_client(self):
        client = MagicMock()
        client.get_top_reactions.return_value = [
            {"term": "NAUSEA", "count": 500},
        ]
        analyzer = AdverseEventAnalyzer(client=client)
        reactions = analyzer.get_top_reactions_for_drug("Tylenol", top_n=5)

        client.get_top_reactions.assert_called_once_with("Tylenol", top_n=5)
        self.assertEqual(len(reactions), 1)


if __name__ == "__main__":
    unittest.main()
