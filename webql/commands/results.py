from ..analyzers.codeql_analyzer import CodeQLAnalyzer


def results_command(sarif_file):
    analyzer = CodeQLAnalyzer()
    return analyzer.parse_sarif_results(sarif_file)
