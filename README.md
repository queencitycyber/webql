<p align="center">
   <img src="jsninja_gh.png" width="500" height="400">
</p>

<p align="center">
   🕵️‍♂️🔍 WebQL
</p>




WebQL is an automated JavaScript analysis engine and workflow orchestration framework for modern web application analysis. It combines the power of static analysis tools like CodeQL with dynamic scanning capabilities to provide comprehensive security insights for web applications.

## 🌟 Features

* 🔍 URL scanning and JavaScript file extraction
* 🧹 Automatic JavaScript beautification
    * 🔪📦 ~~Webcrack~~ & Wakaru coming soon!
* 🗃️ CodeQL database generation
* 🔬 Vulnerability analysis using CodeQL queries
* 📊 Results parsing and presentation
* 🚀 Easy-to-use CLI interface

## 🛠️ Installation

1. To install WebQL and it's dependencies using Poetry, which is useful for development:

```
git clone https://github.com/queencitycyber/webql
cd webql
poetry install
```

2. Activate the virtual environment created by Poetry:

```
poetry shell
```

3. Alternatively, you can run WebQL commands without activating the virtual environment by prefixing them with `poetry run`:

```
poetry run webql scan https://example.com
```

4. If you don't have or don't want to use Poetry, you can use `pipx`:

```
git clone https://github.com/queencitycyber/webql
cd webql
pipx install .
```

5. Docker installation:

... not just yet, but see [Microsoft's codeql-container](https://github.com/microsoft/codeql-container)? Untested but passes sniff test!

## 🚀 Usage

After installation, you can run WebQL using:

```
webql
```

Or:

```
python -m webql
```

### Help Menu

```
Usage: webql [OPTIONS] COMMAND [ARGS]...

  WebQL: An automated JavaScript analysis engine and workflow orchestration
  framework.

Options:
  --debug        Enable debug logging
  --config PATH  Path to config file
  --help         Show this message and exit.

Commands:
  full-analysis  Perform a full analysis on a given URL.
  generate       Generate a CodeQL database for JavaScript analysis.
  parse          Parse files using CodeQL.
  results        Parse and display vulnerability results from a SARIF file.
  scan           Scan URLs or files for JavaScript + webpack & sourcemaps.
  secrets        JS secret and juicy bit scanning.
```

WebQL provides several commands for different stages of analysis.

### Scanning a URL

This command will scan the specified URL, extract JavaScript files, beautify them, generate a CodeQL database, and run CodeQL analysis.

```
webql scan https://example.com
```

Scanning a single URL with aggresive mode (not usually recommended) and specifying an output directory:

_Aggressive Mode pulled directly from zb3's getfrontend found below_. HUGE shoutout!

```
webql scan https://example.com --output-dir ./output --aggressive
```

### Generating a CodeQL Database

This command creates a CodeQL database from the JavaScript files in the specified directory.

```
webql generate ./output --db-name my_analysis
```


### Analyzing the Database

This command runs CodeQL analysis on the generated database and outputs the results in SARIF format.

```
webql parse ./output/my_analysis --output-file results.sarif
```

### Viewing Results

This command parses and displays the vulnerability results from the SARIF file.

```
webql results results.sarif
```

Check out SARIF Explorer for a better view of the results: [SARIF Explorer](https://marketplace.visualstudio.com/items?itemName=trailofbits.sarif-explorer)

### Full Analysis

To perform a full analysis in one go:

```
webql full-analysis https://example.com
```

This command will scan the URL, generate a CodeQL database, perform analysis, and display the results.


### 👨🏼‍⚖️ Trial Run - Full Analysis

Full trial run of OWASP's Juice Shop (excuse the loquacious output, you can turn off in the code if you'd like:) :

```
webql full-analysis https://juice-shop.herokuapp.com
```

![image](https://github.com/user-attachments/assets/8aa61c44-cc0b-438c-a2a3-f6cbb57a84b2)


![image](https://github.com/user-attachments/assets/c49a28d7-1b59-481c-9ed6-095510c7e708)

![image](https://github.com/user-attachments/assets/33677440-f553-49f2-b023-65e0d33ff856)

![image](https://github.com/user-attachments/assets/04d5d3e6-7c52-456e-8fe4-d51fd31c6e24)



### 🧪 Examples and Testing

To ensure WebQL continues to function correctly as we develop and maintain it, we've included a set of example websites and JavaScript files that can be used for testing. These examples cover various scenarios and edge cases that WebQL should handle.

#### Using the Examples

##### Scan a Known Website

This should successfully scan the example.com website and save JavaScript files to the `example_scan` directory.

```
webql scan https://example.com --output-dir ./example_scan
```


##### Analyze Local JavaScript Files

This sequence of commands should analyze the sample JavaScript files provided in the test fixtures, generate a CodeQL database, perform the analysis, and display the results.

```
webql generate ./webql/vulnerable_examples/ --db-name sample_db
webql parse ./sample_db --output-file sample_results.sarif
webql results sample_results.sarif
```


##### Full Analysis of a Test Website

This command runs a full analysis on the OWASP Juice Shop, a purposefully vulnerable web application. It's a good test case for WebQL's ability to detect various vulnerabilities.

```
webql full-analysis https://juice-shop.herokuapp.com
webql full-analysis https://public-firing-range.appspot.com/
```

##### WebQL Vulnerable Examples

WebQL comes with a set of vulnerable JavaScript examples and scripts to test against them. These examples are crucial for demonstrating WebQL's capabilities and for testing purposes.

As WebQL evolves, it's important to keep these examples up-to-date and add new ones as needed:

- Regularly run the example commands to ensure they still work as expected.
- If a website used in an example changes or becomes unavailable, update the example with a new, suitable website.
- Add new examples when implementing new features or handling new edge cases.
- Include examples that demonstrate both successful scans/analyses and how WebQL handles errors or edge cases.

📁 Directory Structure

```
webql/
├── vulnerable_examples/
│   ├── test.js
│   ├── xss_vulnerable.js
│   ├── sql_injection.js
│   └── ... (other vulnerable JS files)
└── scripts/
    └── analyze_examples.py
    └── full_analysis.py
```

The `vulnerable_examples/` directory contains JavaScript files with known vulnerabilities. These files serve as test cases for WebQL's analysis capabilities. Some examples include:

- test.js: A basic file with multiple vulnerability types.
- xss_vulnerable.js: Demonstrates Cross-Site Scripting (XSS) vulnerabilities.
- sql_injection.js: Shows SQL injection vulnerabilities.

#### 🧪 Testing with Vulnerable Examples

##### Using the `analyze_examples.py` Script

The `analyze_examples.py` script in the `scripts/` directory automates the process of analyzing all vulnerable examples.

To run the script:

```
python webql/scripts/analyze_examples.py
```

This script will:

1. Scan each JavaScript file in the `vulnerable_examples/` directory.
2. Generate a CodeQL database for each file.
3. Analyze the database using predefined queries.
4. Display the results


If you find a website or create a JavaScript sample that would make a good test case for WebQL:

1. For websites, add the URL and a brief description to the README in the "Examples and Testing" section.
2. For JavaScript files, add them to the `webql/vulnerable_examples/` or something appropriate directory.
3. Create a new test in the appropriate test file under the `tests/` directory.
4. Update this README section if necessary to include any new usage examples.


By regularly using and updating these examples, we can ensure that WebQL remains robust and effective across a wide range of scenarios.


## 🔮 Future Features

We're constantly working to improve WebQL. Here are some features we're planning to implement:


🔪 ~~Webcrack~~ & Wakaru coming soon!

🌐 Support for additional JavaScript frameworks and libraries

🔧 Custom CodeQL query support

📈 Enhanced reporting capabilities with graphical output

🔄 Continuous monitoring mode for real-time analysis

🔌 Plugin system for extending functionality

🔒 Integration with additional security tools and APIs

🖥️ Web interface for easier interaction and result visualization

### 🤔 Inspired By & Required Reading:
* <https://github.com/zb3/getfrontend>
* <https://news.ycombinator.com/item?id=40855117>
* <https://devtools.tech/blog/understanding-webpacks-require---rid---7VvMusDzMPVh17YyHdyL>
* <https://msrc.microsoft.com/blog/2019/11/vulnerability-hunting-with-semmle-ql-dom-xss/>
* <https://breachforce.net/source-and-sinks>
* <https://medium.com/codex/hunting-for-xss-with-codeql-57f70763b938>
* <https://raz0r.name/articles/using-codeql-to-detect-client-side-vulnerabilities-in-web-applications/>
* <https://medium.com/@rarecoil/spa-source-code-recovery-by-un-webpacking-source-maps-ef830fc2351d>
