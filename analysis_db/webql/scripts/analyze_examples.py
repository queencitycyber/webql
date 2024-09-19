import os
import subprocess
from pathlib import Path


def run_command(command):
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    output, error = process.communicate()
    return output.decode(), error.decode()


def main():
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    examples_dir = project_root / "vulnerable_examples"

    print(f"Current working directory: {os.getcwd()}")
    print(f"Project root: {project_root}")
    print(f"Examples directory: {examples_dir}")
    print(f"Examples directory exists: {examples_dir.exists()}")
    print(f"Contents of project root:")
    for item in project_root.iterdir():
        print(f"  {item}")

    # Ensure the examples directory exists
    if not examples_dir.exists():
        print(f"Error: {examples_dir} does not exist.")
        return

    # Analyze each JavaScript file in the examples directory
    for js_file in examples_dir.glob("*.js"):
        print(f"\nAnalyzing {js_file.name}:")

        # Generate CodeQL database
        db_name = f"{js_file.stem}_db"
        db_path = project_root / db_name
        cmd = f"python -m webql generate {js_file} --db-name {db_name} --overwrite"
        output, error = run_command(cmd)
        print(output)
        if error:
            print(f"Error generating database: {error}")
            continue

        # Parse the database
        sarif_file = project_root / f"{js_file.stem}_results.sarif"
        cmd = f"python -m webql parse {db_path} --output-file {sarif_file}"
        output, error = run_command(cmd)
        print(output)
        if error:
            print(f"Error parsing database: {error}")
            continue

        # Display results
        cmd = f"python -m webql results {sarif_file}"
        output, error = run_command(cmd)
        print(output)
        if error:
            print(f"Error displaying results: {error}")


if __name__ == "__main__":
    main()
