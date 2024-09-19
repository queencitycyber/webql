# webql/utils/js_beautifier.py

import jsbeautifier
from pathlib import Path
from rich.console import Console
import logging

console = Console()
log = logging.getLogger(__name__)


def beautify_js_file(file_path):
    """Beautify a single JavaScript file."""
    file_path = Path(file_path)
    if not file_path.exists() or not file_path.is_file():
        log.warning(f"File not found or not a file: {file_path}")
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        opts = jsbeautifier.default_options()
        opts.indent_size = 2
        opts.space_in_empty_paren = True
        beautified_content = jsbeautifier.beautify(content, opts)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(beautified_content)

        log.info(f"Successfully beautified: {file_path}")
        return True
    except Exception as e:
        log.error(f"Error beautifying {file_path}: {str(e)}")
        return False


def beautify_js_directory(directory_path):
    """Beautify all JavaScript files in a directory and its subdirectories."""
    directory_path = Path(directory_path)
    if not directory_path.is_dir():
        log.error(f"Directory not found: {directory_path}")
        return 0

    js_files = list(directory_path.rglob("*.js"))
    log.info(f"Found {len(js_files)} JavaScript files in {directory_path}")

    beautified_count = 0
    for js_file in js_files:
        if beautify_js_file(js_file):
            beautified_count += 1

    log.info(
        f"Successfully beautified {beautified_count} out of {len(js_files)} files."
    )
    return beautified_count
