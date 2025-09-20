# GEMINI.md

## Project Overview

This project, "dlsu-id-name-mapper," is a Python-based tool designed to scrape a public Google Looker Studio report to map De La Salle University (DLSU) ID numbers to student names.

The core functionality is in `main.py`, which uses `Selenium` with a headless Firefox browser to handle the dynamic, JavaScript-rendered content on the target Looker Studio page. It iterates through a range of potential ID numbers, validates them, and scrapes the corresponding name if a match is found.

A JavaScript file, `main.js`, is also present, which contains a function to validate the checksum of a DLSU ID number, mirroring the logic found in `main.py`.

The primary technologies used are:
*   **Python** (>=3.13)
*   **JavaScript**
*   **Python Libraries**: `selenium`, `webdriver-manager`

## Building and Running

### 1. Setup and Dependencies

The project uses `uv` for package management and requires Python 3.13 or higher.

To install the necessary dependencies, run the following command:
```bash
uv pip install selenium webdriver-manager
```

### 2. Running the Scraper

You can execute the script directly from your terminal.

**Selenium-based Scraper:**
This script is designed to work with the dynamic nature of the Looker Studio report.
```bash
.venv/bin/python main.py
```

## Development Conventions

*   The project's dependencies are managed in the `pyproject.toml` file.
*   ID validation logic is duplicated in both Python (`main.py`) and JavaScript (`main.js`).
