# webql/commands/generate.py

from pathlib import Path
from ..analyzers.codeql_analyzer import CodeQLAnalyzer
from ..utils.js_beautifier import beautify_js_directory
from rich.console import Console
import logging

console = Console()
log = logging.getLogger(__name__)


def generate_command(source_path, db_name, overwrite=False):
    source_path = Path(source_path)
    db_path = Path(db_name)

    # Ensure db_path is absolute
    if not db_path.is_absolute():
        db_path = source_path.parent / db_path

    log.info(f"Generating database from source path: {source_path}")
    log.info(f"Database name: {db_name}")
    log.info(f"Overwrite: {overwrite}")
    log.info(f"Full database path: {db_path}")

    # Beautify JavaScript files
    console.print("[yellow]Beautifying JavaScript files...[/yellow]")
    beautified_count = beautify_js_directory(source_path)
    console.print(f"[green]Beautified {beautified_count} JavaScript files.[/green]")

    # Print a sample of beautified code
    js_files = list(Path(source_path).rglob("*.js"))
    if js_files:
        sample_file = js_files[0]
        with open(sample_file, "r", encoding="utf-8") as f:
            sample_content = f.read()[:500]  # Read first 500 characters
        console.print("[cyan]Sample of beautified JavaScript code:[/cyan]")
        console.print(sample_content)

    analyzer = CodeQLAnalyzer()

    # Create CodeQL database
    console.print("[yellow]Creating CodeQL database...[/yellow]")
    try:
        analyzer.create_database(str(source_path), str(db_path), overwrite=overwrite)
        log.info(f"Database creation completed. Path exists: {db_path.exists()}")
        console.print(
            f"[green]CodeQL database created successfully at {db_path}[/green]"
        )
    except Exception as e:
        error_msg = f"Error creating database: {str(e)}"
        log.exception(error_msg)
        console.print(f"[bold red]{error_msg}[/bold red]")
        raise

    return str(db_path)
