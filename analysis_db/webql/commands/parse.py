from ..analyzers.codeql_analyzer import CodeQLAnalyzer


def parse_command(db_path, output_file):
    analyzer = CodeQLAnalyzer()
    analyzer.analyze_database(db_path, output_file)
