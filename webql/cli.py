import shutil
from pathlib import Path
import subprocess
import requests

import click
from rich.box import MINIMAL, ROUNDED
from rich.console import Console
from rich.logging import RichHandler
from rich.style import Style
from rich.table import Table
from rich.text import Text
from rich.traceback import install

from .commands.generate import generate_command
from .commands.parse import parse_command
from .commands.results import results_command
from .commands.scan import scan_command
from .config import Config
from .exceptions import WebQLException
from urllib.parse import urlparse
from datetime import datetime

import logging

# Install rich traceback handler
install(show_locals=True)

# Set up logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

log = logging.getLogger("webql")
console = Console()


def truncate_string(string, max_length):
    return (string[: max_length - 3] + "...") if len(string) > max_length else string

def get_unique_output_dir(url, base_dir='webql_output'):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('.', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path(base_dir) / f"{domain}_{timestamp}"

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output.decode(), error.decode()

def get_safe_filename(url):
    """Convert URL to a safe filename."""
    parsed_url = urlparse(url)
    return f"{parsed_url.netloc.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def check_url_status(url):
    try:
        response = requests.get(url, allow_redirects=True)
        if response.status_code in [200, 301, 302]:
            return True
        else:
            console.print(f"[bold red]Error: Received status code {response.status_code} for URL {url}[/bold red]")
            return False
    except requests.RequestException as e:
        console.print(f"[bold red]Error: Failed to reach {url}: {e}[/bold red]")
        return False
    
def run_trufflehog(target, output_dir):
    """Run truffleHog scan on the downloaded JS directory and save the results to the output directory."""
    parsed_url = urlparse(target)
    domain = parsed_url.netloc.replace('.', '_')
    output_path = Path(output_dir) / "secrets"
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / f"trufflehog_{domain}_output.txt"
    scan_command = f"trufflehog filesystem --directory {target} --json > {output_file}"
    output, error = run_command(scan_command)
    console.print(output)
    if error:
        raise Exception(f"Error scanning for secrets: {error}")
    log.info(f"Secrets scanning completed. Results saved to {output_file}")



@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--config", type=click.Path(exists=True), help="Path to config file")
@click.pass_context
def cli(ctx, debug, config):
    """WebQL: An automated JavaScript analysis engine and workflow orchestration framework."""
    if debug:
        log.setLevel(logging.DEBUG)
        log.debug("Debug logging enabled")

    ctx.ensure_object(dict)
    ctx.obj["config"] = Config(config_path=config)
    log.debug(f"Loaded configuration: {ctx.obj['config']}")


@cli.command()
@click.argument("targets", nargs=-1, required=True)
@click.option(
    "--output-dir",
    "-o",
    default="webql_output",
    help="Output directory for downloaded files",
)
@click.option(
    "--aggressive",
    is_flag=True,
    help="Enable aggressive mode for more thorough scanning",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--secrets", "-s", is_flag=True, help="Run secrets scanning modules")
@click.pass_context
def scan(ctx, targets, output_dir, aggressive, verbose, secrets):
    """Scan URLs or files for JavaScript + webpack & sourcemaps."""
    try:
        for target in targets:
            if not check_url_status(target):
                return

        log.info(f"Starting scan of {len(targets)} target(s)")
        scan_command(targets, output_dir, aggressive, verbose)
        log.info(f"Scan completed. Results saved to {output_dir}")

        if secrets:
            log.info("Running secrets scanning modules...")
            for target in targets:
                run_trufflehog(target, output_dir)
            log.info("Secrets scanning completed.")

    except WebQLException as e:
        log.error(f"WebQL Error: {str(e)}")
    except Exception as e:
        log.exception("An unexpected error occurred during scan")


@cli.command()
@click.argument('url')
@click.option('--output-dir', default='webql_output', help='Base output directory for analysis')
@click.option("--secrets", "-s", is_flag=True, help="Run secrets scanning modules")
def full_analysis(url, output_dir, secrets):
    """Perform a full analysis on a given URL."""
    try:
        if not check_url_status(url):
            return

        #project_root = Path(__file__).parent.parent
        safe_url_name = get_safe_filename(url)
        output_path = Path.cwd() / output_dir / safe_url_name
        output_path.mkdir(parents=True, exist_ok=True)

        console.print(f"[bold blue]Starting full analysis of {url}[/bold blue]")
        console.print(f"[bold blue]Output directory: {output_path}[/bold blue]")

        # Step 1: Scan the URL
        console.print("[yellow]Step 1: Scanning URL for JavaScript files...[/yellow]")
        scan_cmd = f"python -m webql scan {url} --output-dir {output_path}"
        output, error = run_command(scan_cmd)
        console.print(output)
        if error:
            raise Exception(f"Error during scan: {error}")

        # Step 2: Generate CodeQL database
        console.print("[yellow]Step 2: Generating CodeQL database...[/yellow]")
        db_name = f"{safe_url_name}_db"
        db_path = output_path / db_name
        generate_cmd = f"python -m webql generate {output_path} --db-name {db_path} --overwrite"
        output, error = run_command(generate_cmd)
        console.print(output)
        if error:
            raise Exception(f"Error generating database: {error}")

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
            raise Exception(f"Error parsing database: {error}")

        # Step 4: Display results
        console.print("[yellow]Step 4: Displaying results...[/yellow]")
        results_cmd = f"python -m webql results {sarif_file}"
        output, error = run_command(results_cmd)
        console.print(output)
        if error:
            raise Exception(f"Error displaying results: {error}")

        console.print("[bold green]Full analysis completed successfully![/bold green]")
        console.print(f"[bold green]Results are saved in: {output_path}[/bold green]")

        if secrets:
            log.info("Running secrets scanning modules...")
            run_trufflehog(url, output_path)
            log.info("Secrets scanning completed.")



    except Exception as e:
        console.print(f"[bold red]Error during full analysis: {str(e)}[/bold red]")

@cli.command()
@click.argument('source_path', type=click.Path(exists=True))
@click.option('--db-name', type=click.Path(), help='Name for the CodeQL database')
@click.option('--overwrite', is_flag=True, help='Overwrite existing database')
def generate(source_path, db_name, overwrite):
    """Generate a CodeQL database for JavaScript analysis."""
    try:
        if db_name is None:
            db_name = 'webql_codeql_db'  # Default name if not provided
        source_path = Path(source_path)
        db_path = source_path / db_name if not Path(db_name).is_absolute() else Path(db_name)
        
        result = generate_command(str(source_path), str(db_path), overwrite)
        if result:
            console.print(f"[bold green]CodeQL database generated at: {db_path}[/bold green]")
        else:
            console.print("[bold red]Failed to generate CodeQL database[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error during database generation: {str(e)}[/bold red]")

@cli.command()
@click.argument("db_path", type=click.Path(exists=True))
@click.option(
    "--output-file",
    "-o",
    default="results.sarif",
    help="Output file for analysis results",
)
@click.pass_context
def parse(ctx, db_path, output_file):
    """Parse files using CodeQL."""
    try:
        db_path = Path(db_path)
        output_file = Path(output_file)
        if db_path.is_file():
            db_path = db_path.parent
        parse_command(str(db_path), str(output_file))
        log.info(f"CodeQL analysis completed. Results saved to {output_file}")
    except Exception as e:
        log.exception("An unexpected error occurred during parsing")


@cli.command()
@click.argument('results_file', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['text', 'json']), default='text', help='Output format')
def results(results_file, format):
    """Parse and display vulnerability results from a SARIF file."""
    try:
        vulnerabilities = results_command(results_file)
        
        if vulnerabilities is None:
            console.print("[bold yellow]No vulnerabilities found or error in parsing results.[/bold yellow]")
            return

        if format == 'json':
            console.print_json(data=vulnerabilities)
        else:
            table = Table(title="Vulnerability Results")
            table.add_column("Severity", style="cyan")
            table.add_column("Rule ID", style="magenta")
            table.add_column("Message", style="green")
            table.add_column("Location", style="yellow")

            for severity, vulns in vulnerabilities.items():
                for vuln in vulns:
                    table.add_row(
                        severity.capitalize(),
                        vuln['rule_id'],
                        vuln['message'],
                        vuln['location']
                    )
            
            console.print(table)
        
        console.print("[bold green]Results processing completed[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")


@click.group()
def secrets():
    """JS secret and juicy bit scanning."""
    pass

@click.command()
@click.argument("target", type=click.Path(exists=True))
@click.option(
    "--output-dir",
    "-o",
    default="webql_output",
    help="Base output directory for analysis",
)
def trufflehog(target, output_dir):
    """Scan for secrets and API keys using TruffleHog. You should target your JS directory..."""
    try:
        # Parse the target to get the domain
        parsed_url = urlparse(target)
        domain = parsed_url.netloc.replace('.', '_')
        
        # Create the output directory if it doesn't exist
        output_path = Path(output_dir) / "secrets"
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Define the output file path
        output_file = output_path / f"trufflehog_{domain}_output.txt"
        
        # Run the trufflehog scan command
        scan_command = f"trufflehog filesystem --directory {target} --json > {output_file}"
        output, error = run_command(scan_command)
        console.print(output)
        if error:
            raise Exception(f"Error scanning for secrets: {error}")

        log.info(f"Secrets scanning completed. Results saved to {output_file}")
    except Exception as e:
        log.exception("An unexpected error occurred during secrets scanning")

secrets.add_command(trufflehog)
cli.add_command(secrets)

if __name__ == "__main__":
    cli()