# Code Archaeologist 🔥

> "Every legacy codebase tells a story. Sometimes it's a tragedy, sometimes it's a comedy. Usually it's both."

A powerful CLI tool for analyzing legacy codebases, measuring technical debt, and generating beautiful HTML reports with AI-powered insights.

## Features

- **Multi-language Support** - Automatically detects Python, JavaScript, TypeScript, Go, Java, and more
- **Code Health Analysis** - Cyclomatic complexity, dead code detection, security scanning
- **Dependency Health** - Vulnerability detection, outdated package identification
- **Tech Stack Detection** - Framework identification, era determination (classic vs modern)
- **Technical Debt Heatmap** - Visual representation of problem density by file
- **AI-Powered Reports** - LLM-generated summaries, refactoring priorities, migration paths

## Installation

```bash
# Clone the repository
git clone https://github.com/code-archaeologist/code-archaeologist.git
cd code-archaeologist

# Install with pip
pip install -e .

# Or install with full features
pip install -e ".[full]"
```

## Quick Start

```bash
# Analyze a project (output: ./<project>-analysis-<timestamp>.html)
code-archaeologist ./my-legacy-project

# With verbose output
code-archaeologist ./my-legacy-project -v

# Skip LLM analysis (offline mode)
code-archaeologist ./my-legacy-project --no-llm

# Specify output path
code-archaeologist ./my-legacy-project -o ./reports/analysis.html
```

## Command Options

```
code-archaeologist <project_path> [OPTIONS]

Options:
  -o, --output PATH      Output report path (default: ./archaeology-report.html)
  --llm-backend TEXT     LLM backend: openai, ollama, groq, deepseek, azure
  --llm-api-key TEXT     API key for LLM
  --llm-model TEXT       Model name (default: gpt-4)
  --no-llm              Skip LLM analysis
  --exclude PATHS        Comma-separated directories to exclude
  --config PATH          Config file path
  -v, --verbose         Verbose output
```

## Configuration

Create a `config.json` file for persistent configuration:

```json
{
  "exclude_patterns": [".git", "node_modules", "__pycache__"],
  "llm": {
    "backend": "openai",
    "model": "gpt-4",
    "api_key": "your-key-here"
  },
  "analysis": {
    "max_file_size_kb": 1000,
    "timeout_seconds": 300
  }
}
```

Or use environment variables:
- `LLM_BACKEND`
- `LLM_API_KEY`
- `LLM_MODEL`
- `LLM_BASE_URL`
- `OUTPUT_PATH`

## LLM Backends

### OpenAI (Default)
```bash
code-archaeologist ./project --llm-backend openai --llm-api-key sk-xxx --llm-model gpt-4
```

### Ollama (Local)
```bash
# First, install and start Ollama
brew install ollama
ollama serve

# Pull a model (e.g., llama3, mistral, codellama)
ollama pull llama3

# Run analysis with Ollama
code-archaeologist ./project --llm-backend ollama --llm-model llama3
```

Ollama requires no API key - it runs locally on `http://localhost:11434/v1`.

### Groq / DeepSeek
```bash
code-archaeologist ./project --llm-backend groq --llm-api-key gsk_xxx --llm-model llama-3.1-70b-versatile
code-archaeologist ./project --llm-backend deepseek --llm-api-key sk-xxx --llm-model deepseek-chat
```

### Environment Variables
```bash
export LLM_BACKEND=ollama
export LLM_MODEL=llama3
code-archaeologist ./project
```

## Supported Languages

| Language | Complexity | Dead Code | Security |
|----------|------------|-----------|----------|
| Python   | ✅ radon   | ✅ vulture | ✅ bandit |
| JavaScript/TypeScript | ✅ ESLint | ⚠️ basic | ⚠️ npm audit |
| Go       | ⚠️ basic   | ❌        | ⚠️ govulncheck |
| Other    | ⚠️ basic   | ❌        | ❌        |

## Dependencies

Core dependencies (installed automatically):
- `click` - CLI framework
- `jinja2` - HTML templating
- `pygments` - Syntax highlighting & language detection
- `radon` - Python complexity analysis
- `rich` - Terminal output formatting

Optional dependencies (for full analysis):
- `vulture` - Dead code detection
- `bandit` - Security scanning
- `safety` / `pip-audit` - Dependency vulnerabilities
- `openai` - LLM integration

## Example Output

### Health Score Dashboard
- Overall health score (0-100)
- Language distribution chart
- Complexity breakdown
- Issue categorization

### Tech Stack Analysis
- Detected frameworks (Django, React, etc.)
- Era determination (Classic/Modern)
- Architecture patterns (MVC, Microservices, etc.)

### Technical Debt Heatmap
- File-by-file problem density
- Color-coded severity
- Click to see details

### AI Analysis Report

```
## Technical Debt Summary

This project is like an abandoned theme park from the 90s - the roller coasters
are rusty, the cotton candy machines are breeding something suspicious, but 
you can still smell the nostalgia in the air. The code complexity has broken
through the stratosphere, and those untouchable legacy modules are ticking
time bombs...

[Read the full AI analysis report]
```

## Use Cases

- **Onboarding** - Quickly understand a new codebase
- **Due Diligence** - Assess technical health before acquisitions
- **Planning** - Prioritize refactoring efforts
- **Monitoring** - Track technical debt over time
- **Team Communication** - Share health reports with stakeholders

## License

MIT

## Contributing

Contributions welcome! Please read the contributing guidelines first.