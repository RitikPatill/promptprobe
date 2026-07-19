import typer

from .schema import load_suite
from .runner import LLMRunner
from .report import write_report

app = typer.Typer(help="PromptProbe — LLM prompt regression testing.")


@app.command()
def eval(suite: str = typer.Argument(..., help="Path to YAML test suite")):
    """Run a test suite against an LLM."""
    s = load_suite(suite)
    runner = LLMRunner(s)
    results = runner.run()
    report_path = write_report(s.name, results, model=s.model)
    typer.echo(f"Results: {sum(r.passed for r in results)}/{len(results)} passed")
    typer.echo(f"Report: {report_path}")


@app.command()
def diff(run_a: str = typer.Argument(...), run_b: str = typer.Argument(...)):
    """Compare two JSON result files."""
    typer.echo("diff: not implemented yet")


@app.command(name="list")
def list_runs(results_dir: str = typer.Argument("results")):
    """List saved result files."""
    typer.echo("list: not implemented yet")
