# webql/commands/scan.py

from ..analyzers.javascript_analyzer import JavaScriptAnalyzer
from pathlib import Path
from typing import List, Union

def scan_command(targets: Union[str, List[str]], output_dir: str, *args, **kwargs) -> bool:
    if isinstance(targets, str):
        targets = [targets]
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for target in targets:
        analyzer = JavaScriptAnalyzer(target, output_path)
        analyzer.scan()
    
    return True  # Return True if scan completes successfully