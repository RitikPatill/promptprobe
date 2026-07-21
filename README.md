# PromptProbe — LLM Prompt Evaluation CLI


> **Video walkthrough:** https://youtu.be/_NoOoZDBa8M
> **60-second overview:** https://youtu.be/CgDY2Py8fWQ

> A local CLI that runs YAML-defined prompt test suites against Claude/GPT and detects regressions across versions.

<!-- TODO: replace with a 5-10 second demo gif. Record with ScreenToGif on
     Windows or peek on macOS. Save to docs/demo.gif and update path here. -->
![demo](docs/demo.gif)

## What it is

PromptProbe is a lightweight, local-first CLI for regression-testing LLM prompts. You define test suites in plain YAML — each suite specifies a system prompt, a list of input/expected-output pairs, and a scorer. Running `promptprobe eval` produces a coloured terminal table and a JSON artefact you can diff in CI.

It is intentionally thin: no server, no database, no UI. It installs as a dev dependency into any Python project and slots into a standard CI pipeline with a single workflow step.

## Quickstart

```bash
git clone https://github.com/RitikPatill/promptprobe.git
cd promptprobe
pip install -e .

# Set your API key(s)
export ANTHROPIC_API_KEY=sk-ant-...   # required for Claude models and llm_judge scorer
export OPENAI_API_KEY=sk-...          # optional, for GPT models

# Run the bundled example suite
promptprobe eval examples/qa_suite.yaml

# Compare two result files to detect regressions
promptprobe diff demo/run_a.json demo/run_b.json
```

## Usage

**`promptprobe eval <suite.yaml>`** — runs a suite against the configured model, prints a per-case pass/fail table, and writes a timestamped JSON report to `results/`. Exits `0` when all cases pass, `1` when any fail.

**`promptprobe diff <run_a.json> <run_b.json>`** — compares two result files. Regressions (PASS→FAIL) are printed in red, fixes (FAIL→PASS) in green. Exits `1` on any regression, making it a natural CI gate.

**`promptprobe list [results_dir]`** — lists JSON result files in a directory (default: `results/`).

Suites are plain YAML. The minimal fields are `name`, `system_prompt`, `scorer`, and `cases`:

```yaml
name: basic-qa
model: claude-haiku-4-5-20251001
system_prompt: "You are a concise factual assistant."
scorer: contains
cases:
  - user: "Who created Python?"
    expected: "Guido van Rossum"
  - user: "What is the boiling point of water?"
    expected: "100"
```

Three scorers are available: `exact` (case-insensitive full-string match), `contains` (all comma-separated keywords present), and `llm_judge` (a secondary Claude call rates the response 1-5 against a rubric; pass threshold is 3).

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   PromptProbe                   │
│                                                 │
│  YAML Suite ──► Parser/Schema ──► LLM Runner   │
│                                  (Anthropic /  │
│                                   OpenAI)      │
│                                      │         │
│                                   Scorer       │
│                            (exact / contains / │
│                              llm_judge)        │
│                                      │         │
│                          JSON Report + Rich UI  │
│                          results/run_<ts>.json  │
│                                      │         │
│                          promptprobe diff       │
│                          regression detection   │
└─────────────────────────────────────────────────┘
```

## Project structure

```
promptprobe/
├── src/promptprobe/   # core library: cli, schema, runner, scorers, report, differ
├── tests/             # 53 unit + integration tests (all mocked, no live API calls)
├── examples/          # sample YAML suites (qa_suite, summarisation_suite)
├── demo/              # pre-staged fixture JSON files and VHS tape script
└── pyproject.toml     # package metadata and dependencies
```

## Roadmap

- [ ] Parallel case execution to reduce wall-clock time on large suites
- [ ] `promptprobe watch` — re-run a suite on file change during development
- [ ] HTML report export for sharing results outside the terminal
- [ ] Support for multi-turn conversation test cases
- [ ] PyPI release and `pipx install promptprobe` install path

## License

MIT — see [LICENSE](LICENSE).

---

Built autonomously by [autodev](https://github.com/RitikPatill/autodev),
a multi-agent orchestrator I designed. Each commit in this repo was
authored by me; the implementation work was performed by Sonnet under
the orchestrator's control. Read the orchestrator's README to see how.
