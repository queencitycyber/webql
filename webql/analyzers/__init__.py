"""Analyzers for WebQL."""

from .javascript_analyzer import JavaScriptAnalyzer
from .codeql_analyzer import CodeQLAnalyzer

__all__ = ["JavaScriptAnalyzer", "CodeQLAnalyzer"]
