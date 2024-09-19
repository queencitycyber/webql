# webql/webql/analyzers/codeql_analyzer.py

import subprocess
import json
from pathlib import Path
from rich.console import Console
from urllib.parse import urljoin

console = Console()


class CodeQLAnalyzer:
    def __init__(self, codeql_cli_path="codeql"):
        self.codeql_cli_path = codeql_cli_path

    def create_database(
        self, source_path, db_path, language="javascript", overwrite=False
    ):
        console.print(
            f"[bold blue]Creating CodeQL database for {source_path}[/bold blue]"
        )
        cmd = [
            self.codeql_cli_path,
            "database",
            "create",
            "--quiet",
            db_path,
            f"--language={language}",
            "--source-root",
            source_path,
        ]

        if overwrite:
            cmd.append("--overwrite")

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            console.print(
                f"[bold green]CodeQL database created successfully at {db_path}[/bold green]"
            )
            console.print(f"[dim]Command output:[/dim]\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            console.print(
                f"[bold red]Error creating CodeQL database:[/bold red]\n{e.stderr}"
            )
            raise

    def analyze_database(self, db_path, output_file, query_suite="javascript-lgtm.qls"):
        console.print(f"[bold blue]Analyzing CodeQL database {db_path}[/bold blue]")

        cmd = [
            self.codeql_cli_path,
            "database",
            "analyze",
            "--quiet",
            db_path,
            query_suite,
            "--format=sarif-latest",
            f"--output={output_file}",
        ]

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            console.print(
                f"[bold green]CodeQL analysis completed. Results saved to {output_file}[/bold green]"
            )
            console.print(f"[dim]Command output:[/dim]\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red]Error analyzing CodeQL database:[/bold red]")
            console.print(f"[red]Command: {' '.join(cmd)}[/red]")
            console.print(f"[red]Exit code: {e.returncode}[/red]")
            console.print(f"[red]Standard output: {e.stdout}[/red]")
            console.print(f"[red]Standard error: {e.stderr}[/red]")
            raise

    def parse_sarif_results(self, sarif_file):
        console.print(f"[bold blue]Parsing SARIF results from {sarif_file}[/bold blue]")
        try:
            with open(sarif_file, "r") as f:
                sarif_data = json.load(f)

            results = sarif_data.get("runs", [{}])[0].get("results", [])
            vulnerabilities = {
                "critical": [],
                "high": [],
                "medium": [],
                "low": [],
                "info": [],
            }

            for result in results:
                severity = result.get("properties", {}).get("security-severity", "info")
                if isinstance(severity, str):
                    severity = severity.lower()
                elif isinstance(severity, (int, float)):
                    if severity >= 9.0:
                        severity = "critical"
                    elif severity >= 7.0:
                        severity = "high"
                    elif severity >= 4.0:
                        severity = "medium"
                    elif severity > 0:
                        severity = "low"
                    else:
                        severity = "info"

                location = result.get("locations", [{}])[0].get("physicalLocation", {})
                artifact_location = location.get("artifactLocation", {}).get(
                    "uri", "Unknown"
                )

                # Construct the full URL
                base_url = (
                    sarif_data.get("runs", [{}])[0]
                    .get("originalUriBaseIds", {})
                    .get("SRCROOT", {})
                    .get("uri", "")
                )
                full_url = urljoin(base_url, artifact_location)

                # Get line number
                line_number = location.get("region", {}).get("startLine", "Unknown")

                formatted_location = f"{full_url} (:L{line_number})"

                vulnerabilities[severity].append(
                    {
                        "rule_id": result.get("ruleId", "Unknown"),
                        "message": result.get("message", {}).get("text", "No message"),
                        "location": formatted_location,
                    }
                )

            console.print(f"[bold green]Successfully parsed SARIF results[/bold green]")
            return vulnerabilities
        except json.JSONDecodeError:
            console.print(f"[bold red]Error: Invalid JSON in SARIF file[/bold red]")
            raise
        except Exception as e:
            console.print(f"[bold red]Error parsing SARIF results: {str(e)}[/bold red]")
            raise
