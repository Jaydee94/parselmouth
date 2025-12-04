# Parselmouth

<p align="center">
  <img src="assets/parselmouth_logo.png" alt="Parselmouth Logo" width="300">
</p>

Parselmouth is a powerful CLI tool that uses Google's Gemini AI to analyze documents (text and PDF) and generate meaningful, concise titles. It's designed to help organize files by automatically extracting relevant information like dates and context to create consistent filenames.

## Installation

### Install with pipx (Recommended)

[pipx](https://pipx.pypa.io/) installs the CLI in an isolated environment, making it globally available without affecting your system Python.

1.  Clone the repository:
    ```bash
    git clone https://github.com/jaydee94/parselmouth.git
    cd parselmouth
    ```

2.  Install with pipx:
    ```bash
    pipx install .
    ```

After installation, you can run:
```bash
parselmouth --help
```
### Development Installation

For development or if you want to modify the code:

Prerequisites: Python 3.10+ and Poetry.

1.  Clone the repository:
    ```bash
    git clone https://github.com/jaydee94/parselmouth.git
    cd parselmouth
    ```

2.  Install dependencies:
    ```bash
    poetry install
    ```

3.  Run with poetry:
    ```bash
    poetry run parselmouth --help
    ```

### Enable Shell Auto-Completion

After installation, enable auto-completion:

```bash
parselmouth setup-completion
source ~/.bashrc  # or restart your shell
```

This will automatically detect your shell (bash, zsh, or fish) and install the appropriate completion script.

## Configuration

You need a Google Gemini API key to use Parselmouth. You can provide it via:

1.  **Environment Variable**:
    ```bash
    export PARSELMOUTH_API_KEY="your_api_key_here"
    ```

2.  **Config File**:
    Create a `parselmouth.yaml` file in the project directory or `~/.config/parselmouth/config.yaml`:
    ```yaml
    api-key: "your_api_key_here"
    model: "gemini-2.5-flash"
    include-date: true
    date-format: "YYYY-MM-DD"
    separator: "_"
    ```

3.  **CLI Option**:
    ```bash
    poetry run parselmouth --api-key "your_api_key_here" document.pdf
    ```

## Usage

Parselmouth has two main commands:

### `suggest` - Generate a title suggestion

Analyzes a document and displays the suggested title without modifying the file.

```bash
poetry run parselmouth suggest path/to/document.pdf
```

### `rename` - Rename file with generated title

Analyzes a document and renames it with the suggested title.

```bash
poetry run parselmouth rename path/to/document.pdf
```

Use `--dry-run` to preview the rename without actually changing the file:

```bash
poetry run parselmouth rename --dry-run path/to/document.pdf
```

### Global Options

These options can be used with any command:

| Option | Description | Default |
| :--- | :--- | :--- |
| `--config FILE` | Path to a configuration file. | `parselmouth.yaml` or `~/.config/parselmouth/config.yaml` |
| `--api-key TEXT` | Your Gemini API Key. | Env: `PARSELMOUTH_API_KEY` |
| `--model TEXT` | The Gemini model to use. | `gemini-2.5-flash` |
| `--include-date / --no-include-date` | Whether to include extracted dates in the title. | `True` |
| `--date-format TEXT` | Format for the date in the title. | `YYYY-MM-DD` |
| `--separator TEXT` | Character used to separate words. | `_` |

### Examples

**Suggest a title (default behavior):**
```bash
poetry run parselmouth suggest tests/data/invoice.pdf
# Output: Suggested Title: 2023-10-27_invoice_1023
```

**Rename a file:**
```bash
poetry run parselmouth rename tests/data/invoice.pdf
# Renamed: tests/data/invoice.pdf -> tests/data/2023-10-27_invoice_1023.pdf
```

**Dry-run to preview rename:**
```bash
poetry run parselmouth rename --dry-run tests/data/invoice.pdf
# Would rename: tests/data/invoice.pdf -> tests/data/2023-10-27_invoice_1023.pdf
```

**Kebab-case without date:**
```bash
poetry run parselmouth --separator "-" --no-include-date suggest tests/data/invoice.pdf
# Output: Suggested Title: invoice-1023
```

**Custom date format:**
```bash
poetry run parselmouth --date-format "YYYYMMDD" suggest tests/data/meeting_notes.pdf
# Output: Suggested Title: 20231026_project_alpha_meeting_notes
```

## Development

To run tests (generates sample data first):
```bash
poetry run python scripts/generate_test_data.py
poetry run parselmouth suggest tests/data/invoice.pdf
```
