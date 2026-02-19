"""Tests for the CLI module."""

import json
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

from fda_fact_check.cli import main


class TestCLI(unittest.TestCase):

    @patch("fda_fact_check.cli.OpenFDAClient")
    @patch("sys.stdout", new_callable=StringIO)
    def test_drug_and_reaction_text_output(self, mock_stdout, mock_client_cls):
        client = mock_client_cls.return_value
        client.count_adverse_events.return_value = 1000
        client.count_events_with_reaction.return_value = 5
        client.count_reaction_all_drugs.return_value = 200

        main(["Tylenol", "autism"])

        output = mock_stdout.getvalue()
        self.assertIn("Tylenol", output)
        self.assertIn("autism", output)

    @patch("fda_fact_check.cli.OpenFDAClient")
    @patch("sys.stdout", new_callable=StringIO)
    def test_drug_and_reaction_json_output(self, mock_stdout, mock_client_cls):
        client = mock_client_cls.return_value
        client.count_adverse_events.return_value = 1000
        client.count_events_with_reaction.return_value = 5
        client.count_reaction_all_drugs.return_value = 200

        main(["Tylenol", "autism", "--json"])

        data = json.loads(mock_stdout.getvalue())
        self.assertEqual(data["drug"], "Tylenol")

    @patch("fda_fact_check.cli.OpenFDAClient")
    @patch("sys.stdout", new_callable=StringIO)
    def test_top_reactions_output(self, mock_stdout, mock_client_cls):
        client = mock_client_cls.return_value
        client.get_top_reactions.return_value = [
            {"term": "NAUSEA", "count": 500},
            {"term": "HEADACHE", "count": 300},
        ]

        main(["Tylenol"])

        output = mock_stdout.getvalue()
        self.assertIn("NAUSEA", output)
        self.assertIn("HEADACHE", output)


if __name__ == "__main__":
    unittest.main()
