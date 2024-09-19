import subprocess
from pathlib import Path
from rich.console import Console


console = Console()

class WebcrackAnalyzer:
    def __init__(self, output_dir, verbose=False):
        self.output_dir = Path(output_dir)
        self.verbose = verbose

    def run_webcrack(self, file_path):
        try:
            output_file = file_path.with_name(file_path.stem + "_webcracked.js")
            result = subprocess.run(
                ["webcrack", str(file_path)], capture_output=True, text=True
            )
            output_file.write_text(result.stdout)
            if self.verbose:
                console.print(f"[green]Webcrack processed file:[/green] {output_file}")
            return output_file
        except Exception as e:
            console.print(f"[bold red]Error running webcrack on {file_path}: {e}[/bold red]")
            return None