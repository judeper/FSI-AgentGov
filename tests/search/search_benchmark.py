#!/usr/bin/env python3
"""Benchmark MkDocs Material search findability for FSI-AgentGov."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INDEX = ROOT / "site" / "search" / "search_index.json"
DEFAULT_QUERIES = ROOT / "tests" / "search" / "queries.json"
DEFAULT_ALIASES = ROOT / "docs" / "javascripts" / "search-aliases.json"
STOPWORDS = {"a", "an", "and", "are", "by", "can", "for", "from", "how", "i", "in", "is", "of", "on", "or", "the", "to", "what", "when", "where", "who", "with"}


def norm_text(value: str) -> str:
    clean = value.lower().replace("&", " and ")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", clean)).strip()


def stem(token: str) -> str:
    if len(token) > 5 and token.endswith("ing"):
        return token[:-3]
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 4 and token.endswith("ed"):
        return token[:-2]
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def tokenize(value: str) -> list[str]:
    return [stem(t) for t in re.findall(r"[a-z0-9]+", value.lower()) if t not in STOPWORDS]


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_docs(index_path: Path) -> list[dict[str, str]]:
    data = load_json(index_path)
    docs = data.get("docs", data if isinstance(data, list) else [])
    return [
        {"location": str(d.get("location") or d.get("url") or ""), "title": str(d.get("title") or ""), "text": str(d.get("text") or "")}
        for d in docs
        if isinstance(d, dict)
    ]


def alias_context(query: str, aliases_path: Path) -> tuple[list[str], list[str]]:
    if not aliases_path.exists():
        return [], []
    q_norm = norm_text(query)
    q_tokens = set(tokenize(query))
    expansions: list[str] = []
    urls: list[str] = []
    for entry in load_json(aliases_path):
        phrases = [entry.get("term", ""), entry.get("label", ""), *entry.get("aliases", [])]
        phrase_norms = [norm_text(str(p)) for p in phrases if p]
        phrase_tokens = {token for phrase in phrases for token in tokenize(str(phrase))}
        exact_or_contains = any(q_norm == p or (len(q_norm) >= 3 and (q_norm in p or p in q_norm)) for p in phrase_norms)
        overlap = bool(q_tokens) and len(q_tokens & phrase_tokens) >= min(2, len(q_tokens))
        if exact_or_contains or overlap:
            expansions.extend(str(p) for p in phrases if p)
            if entry.get("url"):
                urls.append(str(entry["url"]).strip("/"))
    return expansions, urls


def doc_model(doc: dict[str, str]) -> dict[str, Any]:
    return {
        "doc": doc,
        "title": Counter(tokenize(doc["title"])),
        "text": Counter(tokenize(doc["text"])),
        "location": Counter(tokenize(doc["location"].replace("/", " ").replace("-", " "))),
        "haystack": norm_text(f"{doc['title']} {doc['text']} {doc['location']}"),
    }


def location_bonus(location: str, matched_urls: list[str]) -> float:
    clean = location.strip("/")
    value = 0.0
    if any(clean.startswith(url) for url in matched_urls):
        value += 120.0
    if clean.startswith("controls/") and "#" not in clean:
        value += 35.0
    elif clean.startswith("reference/regulatory-mappings") and "#" not in clean:
        value += 25.0
    elif clean.startswith("framework/") and "#" not in clean:
        value += 15.0
    if clean.startswith("assessment/pre-session/"):
        value -= 20.0
    if "/control-implementations/" in clean and "#" in clean:
        value -= 8.0
    return value


def score(model: dict[str, Any], query: str, expansions: list[str], matched_urls: list[str]) -> float:
    q_tokens = tokenize(query)
    if not q_tokens:
        return 0.0
    value = location_bonus(model["doc"]["location"], matched_urls)
    q_phrase = norm_text(query)
    if q_phrase and q_phrase in model["haystack"]:
        value += 80.0
    for token in q_tokens:
        value += model["title"].get(token, 0) * 18.0
        value += min(model["text"].get(token, 0), 8) * 3.0
        value += model["location"].get(token, 0) * 5.0
    for phrase in expansions:
        p_norm = norm_text(phrase)
        if p_norm and p_norm in model["haystack"]:
            value += 12.0
        for token in tokenize(phrase):
            value += model["title"].get(token, 0) * 4.0
            value += min(model["text"].get(token, 0), 4) * 0.8
            value += model["location"].get(token, 0) * 1.5
    if "#" not in model["doc"]["location"]:
        value += 0.25
    return value


def rank(models: list[dict[str, Any]], query: str, aliases_path: Path, limit: int) -> list[dict[str, str]]:
    expansions, matched_urls = alias_context(query, aliases_path)
    scored = [(score(model, query, expansions, matched_urls), model["doc"]) for model in models]
    scored = [item for item in scored if item[0] > 0]
    scored.sort(key=lambda item: (-item[0], item[1]["location"]))
    return [doc for _, doc in scored[:limit]]


def validate_queries(queries: Any) -> list[dict[str, Any]]:
    if not isinstance(queries, list):
        raise ValueError("queries.json must be a list")
    for index, query in enumerate(queries, 1):
        if not isinstance(query, dict) or not query.get("q") or not query.get("expect_any"):
            raise ValueError(f"query #{index} must include q and expect_any")
        if not isinstance(query["expect_any"], list):
            raise ValueError(f"query #{index} expect_any must be a list")
    return queries


def run(args: argparse.Namespace) -> int:
    queries = validate_queries(load_json(args.queries))
    aliases = load_json(args.aliases) if args.aliases.exists() else []
    if args.selfcheck:
        index_note = "present" if args.index.exists() else "not present; post-build benchmark skipped"
        print(f"Selfcheck OK: {len(queries)} queries, {len(aliases)} aliases, index {index_note}.")
        return 0
    if not args.index.exists():
        print(f"Search index not found: {args.index}", file=sys.stderr)
        print("Run mkdocs build first, then rerun this benchmark.", file=sys.stderr)
        return 2
    docs = load_docs(args.index)
    if not docs:
        print(f"No documents found in search index: {args.index}", file=sys.stderr)
        return 2
    models = [doc_model(doc) for doc in docs]
    failures: list[tuple[dict[str, Any], list[str]]] = []
    print(f"Search benchmark: {len(queries)} queries against {len(docs)} indexed pages")
    for query in queries:
        top = rank(models, query["q"], args.aliases, args.top)
        top_locations = [doc["location"] for doc in top]
        ok = any(expected in location for expected in query["expect_any"] for location in top_locations)
        print(f"{'PASS' if ok else 'FAIL'} {query['q']}")
        for offset, location in enumerate(top_locations, 1):
            print(f"  {offset}. {location}")
        if not ok:
            failures.append((query, top_locations))
    if failures:
        print("\nFailures:", file=sys.stderr)
        for query, locations in failures:
            print(f"- {query['q']} expected one of {query['expect_any']} in top {args.top}", file=sys.stderr)
            print(f"  got: {locations or '[no matches]'}", file=sys.stderr)
        return 1
    print(f"\nAll {len(queries)} search benchmark queries passed.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark built MkDocs Material search results.")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX, help="Path to site/search/search_index.json")
    parser.add_argument("--queries", type=Path, default=DEFAULT_QUERIES, help="Path to query suite JSON")
    parser.add_argument("--aliases", type=Path, default=DEFAULT_ALIASES, help="Path to search alias JSON")
    parser.add_argument("--top", type=int, default=5, help="Top-N results to inspect")
    parser.add_argument("--selfcheck", action="store_true", help="Validate inputs; skip the built-index benchmark with exit 0")
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(run(parse_args()))
