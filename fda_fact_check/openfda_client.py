"""Client for the OpenFDA Drug Adverse Event API."""

import urllib.parse

import requests

BASE_URL = "https://api.fda.gov/drug/event.json"
DEFAULT_TIMEOUT = 30


class OpenFDAClient:
    """Queries the OpenFDA drug adverse event endpoint."""

    def __init__(self, api_key=None, base_url=BASE_URL, timeout=DEFAULT_TIMEOUT):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

    def _build_params(self, search, limit=None, count_field=None):
        """Build query parameters for the API request."""
        params = {"search": search}
        if self.api_key:
            params["api_key"] = self.api_key
        if limit is not None:
            params["limit"] = limit
        if count_field is not None:
            params["count"] = count_field
        return params

    def _request(self, params):
        """Execute a GET request and return the JSON response."""
        resp = requests.get(self.base_url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get_adverse_events(self, drug_name, limit=10):
        """Return adverse event reports for a given drug name.

        Args:
            drug_name: Brand or generic drug name (e.g. "Tylenol").
            limit: Maximum number of records to return (max 1000).

        Returns:
            dict with ``meta`` and ``results`` keys from the API.
        """
        search = (
            f'patient.drug.medicinalproduct:"{drug_name}"'
        )
        params = self._build_params(search, limit=limit)
        return self._request(params)

    def count_adverse_events(self, drug_name):
        """Return the total number of adverse event reports for a drug.

        The total is extracted from ``meta.results.total`` so that only
        one lightweight request is needed.
        """
        search = (
            f'patient.drug.medicinalproduct:"{drug_name}"'
        )
        params = self._build_params(search, limit=1)
        data = self._request(params)
        return data.get("meta", {}).get("results", {}).get("total", 0)

    def count_events_with_reaction(self, drug_name, reaction):
        """Return the total number of reports where *drug_name* is
        associated with a specific adverse *reaction*.

        Args:
            drug_name: Brand or generic drug name.
            reaction: MedDRA preferred term (e.g. "autism").

        Returns:
            int – total matching report count.
        """
        search = (
            f'patient.drug.medicinalproduct:"{drug_name}"'
            f'+AND+patient.reaction.reactionmeddrapt:"{reaction}"'
        )
        params = self._build_params(search, limit=1)
        data = self._request(params)
        return data.get("meta", {}).get("results", {}).get("total", 0)

    def count_reaction_all_drugs(self, reaction):
        """Return the total number of adverse-event reports across *all*
        drugs for a given reaction term.
        """
        search = f'patient.reaction.reactionmeddrapt:"{reaction}"'
        params = self._build_params(search, limit=1)
        data = self._request(params)
        return data.get("meta", {}).get("results", {}).get("total", 0)

    def get_top_reactions(self, drug_name, top_n=10):
        """Return the top *top_n* reactions reported for a drug.

        Uses the ``count`` parameter of the OpenFDA API.
        """
        search = f'patient.drug.medicinalproduct:"{drug_name}"'
        params = self._build_params(
            search, count_field="patient.reaction.reactionmeddrapt.exact"
        )
        params["limit"] = top_n  # limit applies to count buckets
        data = self._request(params)
        return data.get("results", [])
