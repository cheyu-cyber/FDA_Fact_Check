"""Tests for OpenFDAClient."""

import unittest
from unittest.mock import patch, MagicMock

from fda_fact_check.openfda_client import OpenFDAClient


def _mock_response(json_data, status_code=200):
    """Create a mock ``requests.Response``."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


class TestOpenFDAClient(unittest.TestCase):

    def setUp(self):
        self.client = OpenFDAClient()

    # -- get_adverse_events -------------------------------------------------

    @patch("fda_fact_check.openfda_client.requests.get")
    def test_get_adverse_events_returns_results(self, mock_get):
        payload = {
            "meta": {"results": {"total": 5}},
            "results": [{"id": "1"}, {"id": "2"}],
        }
        mock_get.return_value = _mock_response(payload)

        data = self.client.get_adverse_events("Tylenol", limit=2)

        self.assertEqual(data["results"], [{"id": "1"}, {"id": "2"}])
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertIn("Tylenol", kwargs["params"]["search"])

    # -- count_adverse_events -----------------------------------------------

    @patch("fda_fact_check.openfda_client.requests.get")
    def test_count_adverse_events(self, mock_get):
        payload = {"meta": {"results": {"total": 42}}, "results": [{}]}
        mock_get.return_value = _mock_response(payload)

        total = self.client.count_adverse_events("Aspirin")
        self.assertEqual(total, 42)

    # -- count_events_with_reaction ----------------------------------------

    @patch("fda_fact_check.openfda_client.requests.get")
    def test_count_events_with_reaction(self, mock_get):
        payload = {"meta": {"results": {"total": 3}}, "results": [{}]}
        mock_get.return_value = _mock_response(payload)

        total = self.client.count_events_with_reaction("Tylenol", "autism")
        self.assertEqual(total, 3)
        args, kwargs = mock_get.call_args
        self.assertIn("autism", kwargs["params"]["search"])
        self.assertIn("Tylenol", kwargs["params"]["search"])

    # -- count_reaction_all_drugs ------------------------------------------

    @patch("fda_fact_check.openfda_client.requests.get")
    def test_count_reaction_all_drugs(self, mock_get):
        payload = {"meta": {"results": {"total": 100}}, "results": [{}]}
        mock_get.return_value = _mock_response(payload)

        total = self.client.count_reaction_all_drugs("autism")
        self.assertEqual(total, 100)

    # -- get_top_reactions -------------------------------------------------

    @patch("fda_fact_check.openfda_client.requests.get")
    def test_get_top_reactions(self, mock_get):
        payload = {
            "results": [
                {"term": "NAUSEA", "count": 500},
                {"term": "HEADACHE", "count": 300},
            ]
        }
        mock_get.return_value = _mock_response(payload)

        results = self.client.get_top_reactions("Tylenol", top_n=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["term"], "NAUSEA")

    # -- API key -----------------------------------------------------------

    @patch("fda_fact_check.openfda_client.requests.get")
    def test_api_key_included_when_set(self, mock_get):
        client = OpenFDAClient(api_key="MY_KEY")
        payload = {"meta": {"results": {"total": 1}}, "results": [{}]}
        mock_get.return_value = _mock_response(payload)

        client.count_adverse_events("Ibuprofen")
        _, kwargs = mock_get.call_args
        self.assertEqual(kwargs["params"]["api_key"], "MY_KEY")


if __name__ == "__main__":
    unittest.main()
