"""
Tests for the FDA Adverse Event Fact Checker application.
"""

from unittest.mock import MagicMock, patch

import pytest

from app import app, build_verdict, query_adverse_events


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_response(total: int, status_code: int = 200) -> MagicMock:
    """Return a mock requests.Response whose JSON contains the given total."""
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = {
        "meta": {"results": {"total": total}}
    }
    if status_code >= 400:
        mock_resp.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    else:
        mock_resp.raise_for_status.return_value = None
    return mock_resp


# ---------------------------------------------------------------------------
# Unit tests: build_verdict
# ---------------------------------------------------------------------------

class TestBuildVerdict:
    def test_not_supported_no_drug_reports(self):
        v = build_verdict("Tylenol", "Autism", 0, 0)
        assert v["label"] == "NOT SUPPORTED"
        assert "no adverse event reports" in v["summary"].lower()

    def test_not_supported_no_reaction(self):
        v = build_verdict("Tylenol", "Autism", 10_000, 0)
        assert v["label"] == "NOT SUPPORTED"
        assert "none mention" in v["summary"].lower()

    def test_insufficient_evidence_below_threshold(self):
        v = build_verdict("Tylenol", "Autism", 10_000, 10)
        assert v["label"] == "INSUFFICIENT EVIDENCE"
        assert "10" in v["summary"]

    def test_supported_above_threshold(self):
        v = build_verdict("Ibuprofen", "Heart attack", 50_000, 200)
        assert v["label"] == "SUPPORTED"
        assert "200" in v["summary"]

    def test_percentage_in_summary(self):
        v = build_verdict("Aspirin", "Bleeding", 1000, 100)
        # 100/1000 = 10%
        assert "10.00%" in v["summary"]


# ---------------------------------------------------------------------------
# Unit tests: query_adverse_events
# ---------------------------------------------------------------------------

class TestQueryAdverseEvents:
    @patch("app.requests.get")
    def test_returns_counts(self, mock_get):
        mock_get.side_effect = [_make_response(50_000), _make_response(200)]
        result = query_adverse_events("Ibuprofen", "Heart attack")
        assert result["total_drug_reports"] == 50_000
        assert result["reaction_reports"] == 200
        assert result["error"] is None

    @patch("app.requests.get")
    def test_404_for_reaction_returns_zero(self, mock_get):
        mock_404 = MagicMock()
        mock_404.status_code = 404
        mock_get.side_effect = [_make_response(10_000), mock_404]
        result = query_adverse_events("Tylenol", "Autism")
        assert result["reaction_reports"] == 0
        assert result["error"] is None

    @patch("app.requests.get")
    def test_timeout_returns_error(self, mock_get):
        import requests as req_lib
        mock_get.side_effect = req_lib.exceptions.Timeout
        result = query_adverse_events("Tylenol", "Autism")
        assert result["error"] is not None
        assert "timed out" in result["error"].lower()

    @patch("app.requests.get")
    def test_connection_error_returns_error(self, mock_get):
        import requests as req_lib
        mock_get.side_effect = req_lib.exceptions.ConnectionError
        result = query_adverse_events("Tylenol", "Autism")
        assert result["error"] is not None
        assert "connect" in result["error"].lower()


# ---------------------------------------------------------------------------
# Integration tests: Flask routes
# ---------------------------------------------------------------------------

@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestFlaskRoutes:
    def test_get_index_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"FDA Adverse Event Fact Checker" in resp.data

    def test_post_missing_fields_shows_error(self, client):
        resp = client.post("/", data={"drug_name": "", "reaction": ""})
        assert resp.status_code == 200
        assert b"Please enter both" in resp.data

    @patch("app.query_adverse_events")
    def test_post_shows_verdict(self, mock_query, client):
        mock_query.return_value = {
            "total_drug_reports": 50_000,
            "reaction_reports": 200,
            "error": None,
        }
        resp = client.post(
            "/", data={"drug_name": "Ibuprofen", "reaction": "Heart attack"}
        )
        assert resp.status_code == 200
        assert b"SUPPORTED" in resp.data

    @patch("app.query_adverse_events")
    def test_post_api_error_shows_error(self, mock_query, client):
        mock_query.return_value = {
            "total_drug_reports": 0,
            "reaction_reports": 0,
            "error": "The OpenFDA API request timed out.",
        }
        resp = client.post(
            "/", data={"drug_name": "Tylenol", "reaction": "Autism"}
        )
        assert resp.status_code == 200
        assert b"timed out" in resp.data

    @patch("app.query_adverse_events")
    def test_not_supported_verdict_displayed(self, mock_query, client):
        mock_query.return_value = {
            "total_drug_reports": 100_000,
            "reaction_reports": 0,
            "error": None,
        }
        resp = client.post(
            "/", data={"drug_name": "Tylenol", "reaction": "Autism"}
        )
        assert resp.status_code == 200
        assert b"NOT SUPPORTED" in resp.data
