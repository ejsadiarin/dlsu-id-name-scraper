# DLSU ID Name Scraper

This project is a Python-based tool designed to scrape a public Google Looker Studio report to map De La Salle University (DLSU) ID numbers to student names.

---

## Setup and Dependencies

The project uses `uv` for package management and requires Python 3.13 or higher.

1. Make sure [`uv`](https://docs.astral.sh/uv/getting-started/installation/) is installed on your machine.

2. To install the necessary dependencies, run the following command:
```bash
uv add selenium webdriver-manager
# or uv pip install selenium webdriver-manager
```

---

## Running the Scraper

You can execute the script directly from your terminal.

> [!NOTE]
> the `.venv` directory ensures that it is run on the same environment as where the dependencies are installed

```bash
.venv/bin/python main.py
```

---

## How It Works

The script automates the process of discovering student names based on their ID numbers.

1.  **ID Validation**: The script contains a function `is_dlsu_id()` that implements a checksum algorithm to verify if a given 8-digit number is a syntactically valid DLSU ID number.
2.  **Iteration**: It iterates through a predefined range of numbers. For each number, it first calls `is_dlsu_id()` to check if it's a valid ID format.
3.  **Browser Automation**: For each valid ID, it uses Selenium with a headless Firefox browser to perform the following steps:
    *   Navigates to the target Google Looker Studio URL.
    *   Waits for the page's input field to become available.
    *   Enters the ID number into the input field and submits.
4.  **Data Scraping**: After submitting the ID, the script waits for the results to be displayed on the page. It then:
    *   Selects all potential name-containing elements.
    *   Filters out known placeholder text (e.g., "LAST NAME, FIRST NAME", "ID NUMBER").
    *   Extracts the first valid name that appears.
5.  **Database Storage**:
    *   The scraped ID and name are stored in a local SQLite database file (`students.db`).
    *   The script creates the `students` table if it doesn't exist.
    *   It includes logic to prevent duplicates and to update existing entries if the stored name was a placeholder.
6.  **Error Handling**: The script includes `try...except` blocks to handle timeouts (when a result doesn't appear) and other potential exceptions during the scraping process for a given ID, allowing it to continue with the next ID.

## Technology Stack

*   **Python**: The core language for the scraper.
*   **Selenium**: Used for browser automation to interact with the dynamic JavaScript-heavy website.
*   **webdriver-manager**: To manage the `geckodriver` for Firefox. The script also supports using a local `geckodriver` executable.
*   **SQLite**: For storing the scraped ID numbers and names.
*   **JavaScript**: A separate file (`main.js`) contains a utility function for ID validation, mirroring the Python logic.


## Development Conventions

*   The project's dependencies are managed in the `pyproject.toml` file.
*   ID validation logic is duplicated in both Python (`main.py`) and JavaScript (`main.js`).
