---
name: search-layer
description: >
  Multi-source search and deduplication layer. Integrates Brave Search (web_search),
  Exa, and Tavily to provide high-coverage, high-quality results.
  Triggers on "deep search", "multi-source search", or when high-quality research is needed.
---

# Search Layer — 多源检索协议

三源同级：Brave (`web_search`) + Exa + Tavily。按任务自动选层级。

## Modes

| Mode | Sources | When to use |
|------|---------|-------------|
| **Fast** | Brave `web_search` only | 快速事实查询、简单链接查找 |
| **Deep** | Brave + Exa + Tavily 并行 → 去重 | 项目调研、竞品分析、`github-explorer` 等重型任务 |
| **Answer** | Brave + Tavily (include_answer=true) | 需要"带解释的答案 + 引用"的研究型问题 |

## Execution

### Step 1: Brave (all modes)

Call built-in `web_search` tool. This is always available and free.

### Step 2: Exa + Tavily (Deep / Answer modes)

Run the script to get supplementary results:

```bash
python3 search-layer/scripts/search.py "<query>" --mode deep --num 5
```

Modes: `fast` (Exa only), `deep` (Exa + Tavily parallel), `answer` (Tavily with AI answer).

### Step 3: Merge

Combine Brave results with script output. Deduplicate by canonical URL. Tag each result with source(s).

## Auto-routing Rules

Decide mode by task type — do not ask the user which mode to use:

- **Single fact / quick lookup** → Fast
- **Research, exploration, project analysis, competitive landscape** → Deep
- **"Explain X", "What is the best Y", summary-type questions** → Answer

## Degradation

- Exa 429/5xx → continue with Brave + Tavily
- Tavily 429/5xx → continue with Brave + Exa
- Script fails entirely → Brave `web_search` alone (always works)
- Never block the main workflow on a search source failure

## Output Format

Present merged results as a numbered list with source tags:

```
1. [Title](url) — snippet... `[brave, exa]`
2. [Title](url) — snippet... `[tavily]`
```

When in Answer mode, lead with Tavily's AI answer, then list sources below.
