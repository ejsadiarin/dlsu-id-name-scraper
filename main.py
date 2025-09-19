import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

def is_dlsu_id(id: int) -> bool:
    """
    Verifies if the given 8-digit ID is a valid Lasalian ID.
    Each digit is multiplied by a decreasing weight from 8 to 1.
    The sum must be divisible by 11.
    """
    dlsu_len_str = str(id)
    if len(dlsu_len_str) != 8:
        return False

    total = 0
    for i in range(8):
        total += int(dlsu_len_str[i]) * (8 - i)

    return total % 11 == 0

def main():
    """
    Scrapes lookerstudio (highly dynamic, client-side) populating input tag with a valid DLSU ID number to extract student name.
    """
    url = "https://lookerstudio.google.com/u/0/reporting/cab51826-f8bb-4aed-874e-6b69e61470df/page/p_l1yqh2seid"

    # headless Firefox
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    
    # SQLite database - maybe migrate to postgres?
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, name TEXT)')
    conn.commit()

    # Use a context manager for the driver
    # service = Service(GeckoDriverManager().install()) # Use webdriver-manager NOTE: can be rate limited if trying to run this script with multithreading or multiple worker processes
    service = Service(executable_path='./geckodriver') # safer local option
    with webdriver.Firefox(service=service, options=firefox_options) as driver:
        wait = WebDriverWait(driver, 20)
        # 12328685 - 12328707, 12328839 - 12600001  - 12303003 (cont.)
        # 12328685 - 12328707, 12328839 - 12600001  - 12303003 (cont.)
        # TODO:
        # 12332496 - 12400001
        # 12300000 - 12323004
        # 12000000 - 12300001
        # 12400000 - 12500001
        # 12351598 - 12400001
        # 12306436, 12307238 - get this
        # done: 12305928 - 12351768
        for i in range(12387886, 12500001):
            if is_dlsu_id(i):
                try:
                    # reload the page for each ID to ensure a clean state
                    # PERF: This is slow but reliable.
                    driver.get(url)
                    
                    print(f"Processing ID: {i}")
                    input_elem = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Maglagay ng value']")))
                    
                    input_elem.clear()
                    input_elem.send_keys(str(i))
                    input_elem.send_keys(Keys.ENTER)
                    
                    # filter out placeholders
                    unwanted_results = [
                        "LAST NAME, FIRST NAME",
                        "SUBMITTED (Hard Copy)",
                        "SUBMITTED (Soft Copy)",
                        "Maglagay ng value",
                        "ID NUMBER",
                        "DTCF STATUS",
                        str(i)
                    ]

                    # NOTE: Wait until an element appears that contains a valid name, not just a placeholder
                    # This prevents a race condition where the script grabs headers before the real data loads
                    valid_spans = wait.until(
                        lambda driver: [
                            span for span in driver.find_elements(By.CSS_SELECTOR, "span.cell-value")
                            if span.text.strip() and span.text.strip() not in unwanted_results
                        ]
                    )
                    
                    student_name = valid_spans[0].text.strip() if valid_spans else ""


                    if student_name:
                        try:
                            c.execute("INSERT INTO students (id, name) VALUES (?, ?)", (i, student_name))
                            conn.commit()
                            print(f"SUCCESS - {i}: {student_name}")
                        except sqlite3.IntegrityError:
                            # If students.id already exists, then we check if the existing entry is an unwanted placeholder.
                            c.execute("SELECT name FROM students WHERE id = ?", (i,))
                            existing_name = c.fetchone()[0]
                            
                            if existing_name in unwanted_results:
                                # if stored existing_name is a placeholder, then update with valid existing_name
                                print(f"UPDATING - {i}: Replacing '{existing_name}' with '{student_name}'")
                                c.execute("UPDATE students SET name = ? WHERE id = ?", (student_name, i))
                                conn.commit()
                            else:
                                print(f"SKIPPING - {i}: Already exists with a valid name.")
                    else:
                        print(f"Ignoring ID {i}: No valid name found among visible results.")

                except TimeoutException:
                    print(f"Ignoring ID {i}: No result element found (timeout).")
                except Exception as e:
                    print(f"An unhandled error occurred for ID {i}: {e}")

    conn.close()

if __name__ == "__main__":
    main()
