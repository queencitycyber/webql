# webql/scripts/full_analysis.py

import click
from pathlib import Path
import subprocess
from rich.console import Console
from urllib.parse import urlparse
from datetime import datetime

console = Console()


def run_command(command):
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    output, error = process.communicate()
    return output.decode(), error.decode()


def get_safe_filename(url):
    """Convert URL to a safe filename."""
    parsed_url = urlparse(url)
    return f"{parsed_url.netloc.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


@click.command()
@click.argument("url")
@click.option(
    "--output-dir", default="webql_output", help="Base output directory for analysis"
)
def full_analysis(url, output_dir):
    """Perform a full analysis on a given URL."""
    project_root = Path(__file__).parent.parent.parent
    safe_url_name = get_safe_filename(url)
    output_path = project_root / output_dir / safe_url_name
    output_path.mkdir(parents=True, exist_ok=True)

    console.print(f"[bold blue]Starting full analysis of {url}[/bold blue]")
    console.print(f"[bold blue]Output directory: {output_path}[/bold blue]")

    # Step 1: Scan the URL
    console.print("[yellow]Step 1: Scanning URL for JavaScript files...[/yellow]")
    scan_cmd = f"python -m webql scan {url} --output-dir {output_path}"
    output, error = run_command(scan_cmd)
    console.print(output)
    if error:
        console.print(f"[bold red]Error during scan:[/bold red]\n{error}")
        return

    # Step 2: Generate CodeQL database
    console.print("[yellow]Step 2: Generating CodeQL database...[/yellow]")
    db_name = f"{safe_url_name}_db"
    db_path = output_path / db_name
    generate_cmd = (
        f"python -m webql generate {output_path} --db-name {db_path} --overwrite"
    )
    output, error = run_command(generate_cmd)
    console.print(output)
    if error:
        console.print(f"[bold red]Error generating database:[/bold red]\n{error}")
        return

    console.print(f"[bold cyan]Database path: {db_path}[/bold cyan]")
    console.print(f"[bold cyan]Database exists: {db_path.exists()}[/bold cyan]")

    # Step 3: Analyze the database
    console.print("[yellow]Step 3: Analyzing the database...[/yellow]")
    sarif_file = output_path / f"{safe_url_name}_results.sarif"
    parse_cmd = f"python -m webql parse {db_path} --output-file {sarif_file}"
    console.print(f"[dim]Running command: {parse_cmd}[/dim]")
    output, error = run_command(parse_cmd)
    console.print(output)
    if error:
        console.print(f"[bold red]Error parsing database:[/bold red]\n{error}")
        return

    # Step 4: Display results
    console.print("[yellow]Step 4: Displaying results...[/yellow]")
    results_cmd = f"python -m webql results {sarif_file}"
    output, error = run_command(results_cmd)
    console.print(output)
    if error:
        console.print(f"[bold red]Error displaying results:[/bold red]\n{error}")
        return

    console.print("[bold green]Full analysis completed successfully![/bold green]")
    console.print(f"[bold green]Results are saved in: {output_path}[/bold green]")


if __name__ == "__main__":
    full_analysis()
