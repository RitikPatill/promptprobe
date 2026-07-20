from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .schema import load_suite
from .runner import LLMRunner
from .report import write_report
from .differ import load_report, compare_reports

app = typer.Typer(help="PromptProbe — LLM prompt regression testing.")


def _trunc(s: str, n: int = 40) -> str:
    return s if len(s) <= n else s[:n] + "…"


@app.command()
def eval(suite: str = typer.Argument(..., help="Path to YAML test suite")):
    """Run a test suite against an LLM."""
    s = load_suite(suite)
    runner = LLMRunner(s)
    results = runner.run()
    report_path = write_report(s.name, results, model=s.model)

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID")
    table.add_column("User")
    table.add_column("Expected")
    table.add_column("Response")
    table.add_column("Status")
    table.add_column("Detail")

    for r in results:
        status = "[green]PASS[/green]" if r.passed else "[red]FAIL[/red]"
        table.add_row(
            r.case_id,
            _trunc(r.user),
            _trunc(r.expected),
            _trunc(r.response),
            status,
            r.score_detail,
        )

    console = Console()
    console.print(table)

    pass_count = sum(r.passed for r in results)
    total = len(results)
    score_pct = round(pass_count / total * 100) if total else 0
    console.print(
        f"[bold]Suite: {s.name} | {pass_count}/{total} passed ({score_pct}%)[/bold]"
    )
    console.print(f"Report: {report_path}")

    all_passed = pass_count == total
    raise typer.Exit(code=0 if all_passed else 1)


@app.command(name="list")
def list_runs(results_dir: str = typer.Argument("results")):
    """List saved result JSON files."""
    p = Path(results_dir)
    if not p.exists():
        typer.echo("No results directory found.")
        raise typer.Exit(1)
    files = sorted(p.glob("*.json"))
    if not files:
        typer.echo("No results found.")
        return
    for f in files:
        typer.echo(f.name)


@app.command()
def diff(run_a: Path = typer.Argument(...), run_b: Path = typer.Argument(...)):
    """Compare two JSON result files and highlight regressions."""
    console = Console()
    try:
        report_a = load_report(str(run_a))
        report_b = load_report(str(run_b))
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    result = compare_reports(report_a, report_b)

    table = Table(show_header=True, header_style="bold")
    table.add_column("Case ID")
    table.add_column("User")
    table.add_column("Run A")
    table.add_column("Run B")
    table.add_column("Change")

    for entry in result["regressions"]:
        table.add_row(
            entry["case_id"],
            _trunc(entry["user"]),
            "[green]PASS[/green]",
            "[red]FAIL[/red]",
            "[red]PASS→FAIL[/red]",
        )
    for entry in result["fixes"]:
        table.add_row(
            entry["case_id"],
            _trunc(entry["user"]),
            "[red]FAIL[/red]",
            "[green]PASS[/green]",
            "[green]FAIL→PASS[/green]",
        )
    for entry in result["unchanged"]:
        status = "[green]PASS[/green]" if entry["passed"] else "[red]FAIL[/red]"
        table.add_row(entry["case_id"], "", status, status, "[dim]–[/dim]")

    console.print(table)

    n_reg = len(result["regressions"])
    n_fix = len(result["fixes"])
    console.print(f"[bold]{n_reg} regression(s), {n_fix} fix(es)[/bold]")

    if result["regressions"]:
        raise typer.Exit(1)
