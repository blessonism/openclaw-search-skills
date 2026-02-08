#!/usr/bin/env python3
"""
Multi-source search: Exa + Tavily with mode selection and dedup.
Brave is handled by the agent via built-in web_search (cannot be called from script).

Modes:
  fast   - Exa only (lightweight, low latency)
  deep   - Exa + Tavily parallel (max coverage)
  answer - Tavily search (includes AI-generated answer with citations)

Usage:
  python3 search.py "query" --mode deep --num 5
  python3 search.py "query" --mode answer
"""

import json
import sys
import argparse
import os
import concurrent.futures
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests


def _find_tools_md() -> str | None:
    """Walk up from CWD / known locations to find TOOLS.md."""
    candidates = [
        os.path.join(os.getcwd(), "TOOLS.md"),
        os.path.expanduser("~/.openclaw/workspace/TOOLS.md"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def get_keys():
    keys = {}
    tools_md = _find_tools_md()
    if tools_md:
        try:
            with open(tools_md) as f:
                for line in f:
                    if "**Exa**:" in line:
                        keys["exa"] = line.split("`")[1]
                    elif "**Tavily**:" in line:
                        keys["tavily"] = line.split("`")[1]
        except (FileNotFoundError, IndexError):
            pass
    # Env vars override file
    if v := os.environ.get("EXA_API_KEY"):
        keys["exa"] = v
    if v := os.environ.get("TAVILY_API_KEY"):
        keys["tavily"] = v
    return keys


def normalize_url(url: str) -> str:
    """Canonical URL for dedup: strip utm_*, anchors, trailing slash."""
    try:
        p = urlparse(url)
        qs = {k: v for k, v in parse_qs(p.query).items() if not k.startswith("utm_")}
        clean = urlunparse((p.scheme, p.netloc, p.path.rstrip("/"), p.params,
                            urlencode(qs, doseq=True) if qs else "", ""))
        return clean
    except Exception:
        return url.rstrip("/")


def search_exa(query: str, key: str, num: int = 5) -> list:
    try:
        r = requests.post(
            "https://api.exa.ai/search",
            headers={"x-api-key": key, "Content-Type": "application/json"},
            json={"query": query, "numResults": num, "type": "auto"},
            timeout=20,
        )
        r.raise_for_status()
        return [
            {
                "title": res.get("title", ""),
                "url": res["url"],
                "snippet": res.get("text", res.get("snippet", "")),
                "source": "exa",
            }
            for res in r.json().get("results", [])
        ]
    except Exception as e:
        print(f"[exa] error: {e}", file=sys.stderr)
        return []


def search_tavily(query: str, key: str, num: int = 5, include_answer: bool = False) -> dict:
    """Returns {"results": [...], "answer": str|None}."""
    try:
        payload = {
            "query": query,
            "max_results": num,
            "include_answer": include_answer,
        }
        r = requests.post(
            "https://api.tavily.com/search",
            headers={"Content-Type": "application/json"},
            json={"api_key": key, **payload},
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        results = [
            {
                "title": res.get("title", ""),
                "url": res["url"],
                "snippet": res.get("content", ""),
                "source": "tavily",
            }
            for res in data.get("results", [])
        ]
        return {"results": results, "answer": data.get("answer")}
    except Exception as e:
        print(f"[tavily] error: {e}", file=sys.stderr)
        return {"results": [], "answer": None}


def dedup(results: list) -> list:
    seen = {}
    out = []
    for r in results:
        key = normalize_url(r["url"])
        if key not in seen:
            seen[key] = r
            out.append(r)
        else:
            existing = seen[key]
            src = existing["source"]
            if r["source"] not in src:
                existing["source"] = f"{src}, {r['source']}"
    return out


def main():
    ap = argparse.ArgumentParser(description="Multi-source search (Exa + Tavily)")
    ap.add_argument("query", help="Search query")
    ap.add_argument("--mode", choices=["fast", "deep", "answer"], default="deep",
                    help="fast=Exa only | deep=Exa+Tavily | answer=Tavily with AI answer")
    ap.add_argument("--num", type=int, default=5, help="Results per source (default 5)")
    args = ap.parse_args()

    keys = get_keys()
    all_results = []
    answer_text = None

    if args.mode == "fast":
        if "exa" not in keys:
            print('{"error": "Exa API key not found. Set EXA_API_KEY env or add to TOOLS.md"}')
            sys.exit(1)
        all_results = search_exa(args.query, keys["exa"], args.num)

    elif args.mode == "deep":
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures = {}
            if "exa" in keys:
                futures["exa"] = pool.submit(search_exa, args.query, keys["exa"], args.num)
            if "tavily" in keys:
                futures["tavily"] = pool.submit(search_tavily, args.query, keys["tavily"], args.num)
            for name, fut in futures.items():
                res = fut.result()
                if isinstance(res, dict):
                    all_results.extend(res.get("results", []))
                else:
                    all_results.extend(res)

    elif args.mode == "answer":
        if "tavily" not in keys:
            print('{"error": "Tavily API key not found. Set TAVILY_API_KEY env or add to TOOLS.md"}')
            sys.exit(1)
        tav = search_tavily(args.query, keys["tavily"], args.num, include_answer=True)
        all_results = tav["results"]
        answer_text = tav.get("answer")

    deduped = dedup(all_results)

    output = {"mode": args.mode, "count": len(deduped), "results": deduped}
    if answer_text:
        output["answer"] = answer_text

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
