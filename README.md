# PromptProbe

LLM prompt regression testing — define test suites in YAML, run them against Claude or GPT, catch regressions before they reach production.

## What works (M3)

- `LLMRunner` dispatches to Anthropic (`claude*`) or OpenAI (`gpt*`) based on model name prefix
- Three scorers fully implemented and unit-tested (no real API calls in tests):
  - `exact` — case-insensitive full-string match
  - `contains` — all comma-separated keywords must appear in the response
  - `llm_judge` — secondary Claude call rates 1–5 against a rubric; pass if ≥ 3
- `write_report()` saves `results/run_<timestamp>.json` with suite summary and per-case details
- `promptprobe eval <suite.yaml>` now calls a real LLM, scores each case, writes a JSON report, and prints a summary
- 12 unit tests across `test_scorers.py` and `test_runner.py`; all pass with mocked LLM clients

## What works (M2)

- YAML test-suite schema defined with `Suite` and `Case` dataclasses in `src/promptprobe/schema.py`
- `load_suite(path)` parses and validates YAML files with clear error messages for every invalid state
- Three scorers recognised: `exact`, `contains`, `llm_judge` — validation enforced at load time
- `SuiteValidationError` raised with human-readable messages pointing to the exact field
- `temperature` defaults to `0.0`; case `id` is auto-assigned as `case_{n}` when omitted
- Test suite in `tests/test_schema.py` covers happy path and all major error conditions (no network calls)
- `pytest==8.2.2` added to `requirements.txt`

## What works (M1)

- Python package scaffold under `src/promptprobe/` with `pyproject.toml` entry point
- `promptprobe` CLI is installable and responds to `--help`
- Three subcommands registered: `eval`, `diff`, `list` — all currently print "not implemented yet"
- Dependencies declared and pinned in `requirements.txt` (Typer, Rich, anthropic, openai, PyYAML)
- MIT license and `.gitignore` in place

Everything below the horizontal line describes the planned interface. Sections marked `<!-- TODO -->` require implementation before they are accurate.

---

## What is PromptProbe

PromptProbe is a lightweight, local-first CLI tool for evaluating and regression-testing LLM prompts. You define test suites in plain YAML — each suite contains a system prompt, a list of input/expected-output pairs, and a scorer. Run `promptprobe eval my_suite.yaml` and get a rich terminal report plus a JSON artefact you can diff in CI. Every team shipping LLM features eventually writes ad-hoc scripts to check whether a new system prompt is "better" than the old one; PromptProbe formalises that loop into a repeatable, versionable workflow with no server, no database, and no UI.

## Installation

```bash
pip install -e .
```

Run from the repo root. Requires Python 3.10+.

## Quick start

Create a test suite YAML file (e.g. `suites/greeting.yaml`):

```yaml
name: greeting_test
system_prompt: "You are a friendly assistant. Always greet the user by name."
model: claude-haiku-4-5-20251001
temperature: 0.0
scorer: contains
cases:
  - user: "My name is Alice."
    expected: "Alice"
  - user: "My name is Bob."
    expected: "Bob"
```

Then run the suite:

```bash
promptprobe eval suites/greeting.yaml
```

## CLI reference

| Subcommand | Arguments | Description |
|---|---|---|
| `eval` | `suite` (path to YAML) | Run a test suite against an LLM and print results |
| `diff` | `run_a`, `run_b` (JSON paths) | Compare two result files and show regressions |
| `list` | `results_dir` (default: `results/`) | List saved result JSON files |

<!-- TODO: add --model, --output, --threshold flags once implemented -->

## Scoring

- **`exact`** — Case-insensitive full-string match between the LLM response and the expected value.
- **`contains`** — All comma-separated tokens in `expected` must appear in the response (case-insensitive). E.g. `expected: "bonjour, monde"` checks for both words.
- **`llm_judge`** — A secondary Claude call rates the response 1–5 against a rubric; score ≥ 3 is a pass. Set `scorer: llm_judge` and write a natural-language rubric in each `expected` field.

## CI integration

Every `promptprobe eval` run writes a timestamped JSON artefact to `results/run_<timestamp>.json`. Store these as CI artefacts and use `promptprobe diff run_a.json run_b.json` to detect which cases flipped between pass and fail across prompt versions. The `results/` directory is excluded from version control by default.

## Architecture

```
promptprobe/
├── src/
│   └── promptprobe/
│       ├── __init__.py     # package version
│       ├── __main__.py     # python -m promptprobe entry point
│       ├── cli.py          # Typer app — eval / diff / list subcommands
│       ├── schema.py       # Suite/Case dataclasses + load_suite() + SuiteValidationError
│       ├── runner.py       # LLMRunner — dispatches to Anthropic or OpenAI, returns RunResult list
│       ├── scorers.py      # score_exact, score_contains, score_llm_judge
│       └── report.py       # write_report() — saves results/run_<timestamp>.json
├── tests/
│   ├── __init__.py
│   ├── test_schema.py      # unit tests for schema loader (no network calls)
│   ├── test_scorers.py     # unit tests for all three scorers (mocked LLM)
│   ├── test_runner.py      # dispatch and run() integration tests (mocked LLM)
│   └── fixtures/           # YAML fixtures for tests
├── pyproject.toml          # build config and dependency declarations
├── requirements.txt        # pinned dependencies (includes pytest)
├── LICENSE                 # MIT
└── .gitignore
```

## Roadmap

- **M1** ✓ — package scaffold, CLI entry point, subcommand stubs
- **M2** ✓ — YAML schema (`Suite`/`Case` dataclasses), `load_suite()` parser, `SuiteValidationError`, unit tests
- **M3** ✓ — LLM runner (Anthropic + OpenAI), all three scorers, JSON result writer, `eval` wired end-to-end
- **M4** — `diff` subcommand, regression detection, Rich terminal table output
- **M5** — configurable thresholds, CI exit codes
- **M6** — example suites, full test coverage, PyPI release

## License

MIT — see [LICENSE](LICENSE).
