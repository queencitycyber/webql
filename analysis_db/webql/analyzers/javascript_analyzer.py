import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import json
from pathlib import Path
from rich.progress import Progress
from rich.console import Console

from .webcrack_analyzer import WebcrackAnalyzer

console = Console()

class JavaScriptAnalyzer:
    def __init__(self, base_url, output_dir, aggressive=False, verbose=False):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.aggressive = aggressive
        self.verbose = verbose
        self.session = requests.Session()
        self.visited_urls = set()
        self.progress = Progress()
        self.main_task_id = None
        self.domain = urlparse(base_url).netloc
        self.webcrack_analyzer = WebcrackAnalyzer(output_dir, verbose)

    def scan(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with self.progress:
            self.main_task_id = self.progress.add_task("[green]Scanning...", total=1)
            self._scan_url(self.base_url)
        console.print("[bold green]Scan completed![/bold green]")

    def _scan_url(self, url):
        if url in self.visited_urls:
            return
        self.visited_urls.add(url)

        if self.verbose:
            console.print(f"[cyan]Scanning URL:[/cyan] {url}")

        try:
            response = self.session.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            console.print(f"[bold red]Error:[/bold red] Failed to fetch {url}: {e}")
            return

        content_type = response.headers.get("Content-Type", "").lower()
        if "html" in content_type:
            self._process_html(response.text, url)
        elif "javascript" in content_type:
            self._process_javascript(response.text, url)
        elif "json" in content_type:
            self._process_json(response.text, url)
        else:
            if self.verbose:
                console.print(
                    f"[yellow]Skipping unsupported content type:[/yellow] {content_type} for {url}"
                )

        self.progress.update(self.main_task_id, advance=1, total=len(self.visited_urls))

    def _process_html(self, html_content, url):
        if self.verbose:
            console.print(f"[magenta]Processing HTML:[/magenta] {url}")

        soup = BeautifulSoup(html_content, "html.parser")

        script_tags = soup.find_all("script", src=True)
        if self.verbose:
            console.print(f"[blue]Found {len(script_tags)} script tags[/blue]")

        for script in script_tags:
            script_url = urljoin(url, script["src"])
            self._scan_url(script_url)

        import_maps = soup.find_all("script", type="importmap")
        if self.verbose:
            console.print(f"[blue]Found {len(import_maps)} import maps[/blue]")

        for import_map in import_maps:
            self._process_import_map(import_map.string, url)

        if self.aggressive:
            if self.verbose:
                console.print(
                    "[yellow]Running in aggressive mode, looking for additional JS files[/yellow]"
                )
            js_patterns = [r"\.js", r"\.mjs", r"\.ts", r"\.jsx", r"\.tsx"]
            for pattern in js_patterns:
                for match in re.finditer(pattern, html_content):
                    potential_url = self._extract_url(html_content, match.start())
                    if potential_url:
                        full_url = urljoin(url, potential_url)
                        if self.verbose:
                            console.print(
                                f"[blue]Found potential JS file:[/blue] {full_url}"
                            )
                        self._scan_url(full_url)

    def _process_javascript(self, js_content, url):
        if self.verbose:
            console.print(f"[magenta]Processing JavaScript:[/magenta] {url}")

        parsed_url = urlparse(url)
        file_name = f"{self.domain}_{parsed_url.path.split('/')[-1]}"
        file_path = self.output_dir / file_name
        file_path.write_text(js_content)

        if self.verbose:
            console.print(f"[green]Saved JavaScript file:[/green] {file_path}")

        # Run webcrack on the saved JavaScript file
        webcracked_file = self.webcrack_analyzer.run_webcrack(file_path)

        # Use the webcracked file for further analysis if available
        if webcracked_file:
            file_path = webcracked_file

        source_map_url = self._find_source_map_url(js_content)
        if source_map_url:
            full_source_map_url = urljoin(url, source_map_url)
            self._fetch_source_map(full_source_map_url)

        dynamic_imports = re.findall(
            r'import\s*\(\s*[\'"`](.+?)[\'"`]\s*\)', js_content
        )
        if self.verbose:
            console.print(f"[blue]Found {len(dynamic_imports)} dynamic imports[/blue]")
        for imp in dynamic_imports:
            self._scan_url(urljoin(url, imp))

        chunk_patterns = [
            r'__webpack_require__\.e\s*\(\s*[\'"`](.+?)[\'"`]\s*\)',
            r'webpackJsonp\s*\(\s*[\'"`](.+?)[\'"`]\s*\)',
            r'__webpack_require__\.t\s*\(\s*[\'"`](.+?)[\'"`]\s*\)',
        ]
        for pattern in chunk_patterns:
            chunks = re.finditer(pattern, js_content)
            if self.verbose:
                console.print(
                    f"[blue]Checking for webpack chunks with pattern:[/blue] {pattern}"
                )
            for match in chunks:
                chunk_url = urljoin(url, match.group(1) + ".js")
                if self.verbose:
                    console.print(f"[blue]Found webpack chunk:[/blue] {chunk_url}")
                self._scan_url(chunk_url)

    def _process_json(self, json_content, url):
        if self.verbose:
            console.print(f"[magenta]Processing JSON:[/magenta] {url}")

        try:
            data = json.loads(json_content)

            if "pages" in data and isinstance(data["pages"], dict):
                if self.verbose:
                    console.print("[blue]Detected Next.js build manifest[/blue]")
                for page, files in data["pages"].items():
                    if self.verbose:
                        console.print(f"[blue]Processing page:[/blue] {page}")
                    for file in files:
                        self._scan_url(urljoin(url, file))

            if "entry" in data and "routes" in data:
                if self.verbose:
                    console.print("[blue]Detected Remix manifest[/blue]")
                for entry in data["entry"].values():
                    self._scan_url(urljoin(url, entry))
                for route, route_data in data["routes"].items():
                    if self.verbose:
                        console.print(f"[blue]Processing route:[/blue] {route}")
                    if "imports" in route_data:
                        for imp in route_data["imports"]:
                            self._scan_url(urljoin(url, imp))

        except json.JSONDecodeError:
            console.print(
                f"[bold red]Error:[/bold red] Failed to parse JSON from {url}"
            )

    def _process_import_map(self, import_map_content, base_url):
        if self.verbose:
            console.print(f"[magenta]Processing import map from:[/magenta] {base_url}")

        try:
            import_map = json.loads(import_map_content)
            for specifier, address in import_map.get("imports", {}).items():
                if self.verbose:
                    console.print(
                        f"[blue]Found import:[/blue] {specifier} -> {address}"
                    )
                self._scan_url(urljoin(base_url, address))
        except json.JSONDecodeError:
            console.print(
                f"[bold red]Error:[/bold red] Failed to parse import map from {base_url}"
            )

    def _find_source_map_url(self, content):
        match = re.search(r"//# sourceMappingURL=(.+)$", content, re.MULTILINE)
        if match and self.verbose:
            console.print(f"[blue]Found source map URL:[/blue] {match.group(1)}")
        return match.group(1) if match else None

    def _fetch_source_map(self, url):
        if self.verbose:
            console.print(f"[magenta]Fetching source map:[/magenta] {url}")

        try:
            response = self.session.get(url)
            response.raise_for_status()
            parsed_url = urlparse(url)
            file_name = f"{self.domain}_{parsed_url.path.split('/')[-1]}"
            file_path = self.output_dir / file_name
            file_path.write_text(response.text)
            if self.verbose:
                console.print(f"[green]Saved source map:[/green] {file_path}")
        except requests.RequestException as e:
            console.print(
                f"[bold red]Error:[/bold red] Failed to fetch source map {url}: {e}"
            )

    def _extract_url(self, content, start_index):
        end_index = content.find('"', start_index)
        if end_index == -1:
            end_index = content.find("'", start_index)
        return content[start_index:end_index] if end_index != -1 else None
