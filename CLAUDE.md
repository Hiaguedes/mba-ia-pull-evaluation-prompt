# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

MBA challenge: pull a low-quality prompt from LangSmith Hub, optimize it using prompt engineering techniques, push it back, and evaluate it against 5 metrics — all must score ≥ 0.8.

## Commands

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Workflow (in order)
python src/pull_prompts.py    # Pull v1 prompt from LangSmith Hub
python src/push_prompts.py    # Push optimized v2 prompt to LangSmith Hub
python src/evaluate.py        # Run evaluation — all 5 metrics must be >= 0.8

# Tests
pytest tests/test_prompts.py
pytest tests/test_prompts.py -v --tb=short  # single file with details
```

Scripts must be run from the project root (not from `src/`), as paths like `datasets/bug_to_user_story.jsonl` are relative to root.

## Environment Variables

Copy `.env.example` to `.env` and fill in:
- `LANGSMITH_API_KEY` + `LANGSMITH_PROJECT` + `USERNAME_LANGSMITH_HUB`
- Either `OPENAI_API_KEY` (for OpenAI) or `GOOGLE_API_KEY` (for Gemini)
- `LLM_PROVIDER` = `openai` or `google`
- `LLM_MODEL` = model for generating answers (e.g. `gpt-4o-mini`, `gemini-2.5-flash`)
- `EVAL_MODEL` = model for LLM-as-Judge evaluation (e.g. `gpt-4o`, `gemini-2.5-flash`)

## Architecture

### Data flow

```
LangSmith Hub (leonanluppi/bug_to_user_story_v1)
    → pull_prompts.py → prompts/bug_to_user_story_v1.yml
    
prompts/bug_to_user_story_v2.yml (manually optimized)
    → push_prompts.py → LangSmith Hub ({username}/bug_to_user_story_v2)

evaluate.py:
  1. Loads datasets/bug_to_user_story.jsonl → creates LangSmith dataset
  2. Pulls prompt from Hub via hub.pull()
  3. Runs each of 15 examples through: prompt | LLM
  4. Scores each response with metrics.py (LLM-as-Judge)
  5. Reports 5 metrics: Helpfulness, Correctness, F1-Score, Clarity, Precision
```

### Key relationships

- `utils.py` — shared helpers: `get_llm()` (main LLM), `get_eval_llm()` (judge LLM), `load_yaml()`, `save_yaml()`, `check_env_vars()`, `validate_prompt_structure()`
- `metrics.py` — 3 general metrics (`evaluate_f1_score`, `evaluate_clarity`, `evaluate_precision`) + 4 bug-to-user-story-specific ones. All use LLM-as-Judge (calls `get_eval_llm()`). Helpfulness = avg(clarity, precision); Correctness = avg(f1, precision).
- `evaluate.py` — orchestration: imports `get_llm` from `utils` (via local wrapper), `evaluate_f1_score/clarity/precision` from `metrics`. Runs `src/` scripts with `sys.path` pointing to `src/`.
- `tests/test_prompts.py` — validates `prompts/bug_to_user_story_v2.yml` structure; uses `validate_prompt_structure()` from `utils`.

### Prompt YAML schema (`prompts/bug_to_user_story_v2.yml`)

Required fields validated by `validate_prompt_structure()`:
- `description` — string
- `system_prompt` — non-empty, no `TODO`
- `version` — string
- `techniques_applied` — list with at least 2 items

The prompt receives `{bug_report}` as the input variable (from dataset `inputs.bug_report`).

### What needs to be implemented

- `src/pull_prompts.py` — function bodies are stubs (`...`)
- `src/push_prompts.py` — function bodies are stubs (`...`)
- `prompts/bug_to_user_story_v2.yml` — must be created with optimized prompt
- `tests/test_prompts.py` — 6 test methods are stubs; must validate the v2 YAML

### What is already complete (do not modify)

- `src/evaluate.py`, `src/metrics.py`, `src/utils.py`
- `datasets/bug_to_user_story.jsonl` (15 examples: 5 simple, 7 medium, 3 complex)
