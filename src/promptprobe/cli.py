import typer

app = typer.Typer(help="PromptProbe — LLM prompt regression testing.")


@app.command()
def eval(suite: str = typer.Argument(..., help="Path to YAML test suite")):
    """Run a test suite against an LLM."""
    typer.echo("eval: not implemented yet")


@app.command()
def diff(run_a: str = typer.Argument(...), run_b: str = typer.Argument(...)):
    """Compare two JSON result files."""
    typer.echo("diff: not implemented yet")


@app.command(name="list")
def list_runs(results_dir: str = typer.Argument("results")):
    """List saved result files."""
    typer.echo("list: not implemented yet")
