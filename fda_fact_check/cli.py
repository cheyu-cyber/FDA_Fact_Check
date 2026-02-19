"""Command-line interface for FDA Fact Check."""

import argparse
import json
import sys

from .analyzer import AdverseEventAnalyzer
from .openfda_client import OpenFDAClient


def build_parser():
    parser = argparse.ArgumentParser(
        prog="fda-fact-check",
        description=(
            "Fact-check adverse event claims about drugs using the "
            "OpenFDA API."
        ),
    )
    parser.add_argument(
        "drug",
        help='Drug name to look up (e.g. "Tylenol")',
    )
    parser.add_argument(
        "reaction",
        nargs="?",
        default=None,
        help=(
            'Adverse reaction to check (e.g. "autism"). '
            "If omitted, the top reactions for the drug are shown."
        ),
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Number of top reactions to show (default: 10).",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Optional OpenFDA API key for higher rate limits.",
    )
    parser.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        help="Output raw JSON instead of a human-readable summary.",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    client = OpenFDAClient(api_key=args.api_key)
    analyzer = AdverseEventAnalyzer(client=client)

    try:
        if args.reaction:
            result = analyzer.check_drug_reaction(args.drug, args.reaction)
            if args.output_json:
                print(json.dumps(result, indent=2))
            else:
                print(result["summary"])
        else:
            reactions = analyzer.get_top_reactions_for_drug(
                args.drug, top_n=args.top_n,
            )
            if args.output_json:
                print(json.dumps(reactions, indent=2))
            else:
                print(f"Top {args.top_n} reported reactions for {args.drug}:\n")
                for i, entry in enumerate(reactions, 1):
                    print(f"  {i}. {entry['term']} ({entry['count']:,} reports)")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
