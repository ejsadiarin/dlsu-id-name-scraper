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
    NOTE: If error occurred when processing a valid dlsu ID, then most likely the students.name is 'No data' (meaning he/she is graduated or not in DLSU anymore)
    
    Possible anomalies in students.name:
    - NOT SUBMITTED 
    - all not in caps (ex. Submitted, not in the list, etc.)
    """


    url = "https://lookerstudio.google.com/u/0/reporting/cab51826-f8bb-4aed-874e-6b69e61470df/page/p_l1yqh2seid"

    # Set up headless Firefox
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    
    # Set up SQLite database
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, name TEXT)')
    conn.commit()

    # Use a context manager for the driver
    with webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options) as driver:
        wait = WebDriverWait(driver, 20)
        
        print("Loading page once...")
        driver.get(url)
        
        # Find the input element once after the initial page load.
        input_elem = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Maglagay ng value']")))

        for i in range(11901632, 12600001):
            if is_dlsu_id(i):
                try:
                    print(f"Processing ID: {i}")

                    # Get a reference to the current results before triggering a new search
                    old_results = driver.find_elements(By.CSS_SELECTOR, "span.cell-value")

                    # Input the new ID
                    input_elem.clear()
                    input_elem.send_keys(str(i))
                    input_elem.send_keys(Keys.ENTER)

                    # Wait for the old results to become stale. This confirms the page has started updating.
                    if old_results:
                        try:
                            wait.until(EC.staleness_of(old_results[0]))
                        except TimeoutException:
                            # This can happen if the page doesn't update. We'll log a warning
                            # and let the subsequent wait handle the timeout.
                            print(f"Warning: Page state did not change for ID {i}.")
                    
                    # Now, wait for the new results to appear and process them
                    try:
                        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "span.cell-value")))
                        value_spans = driver.find_elements(By.CSS_SELECTOR, "span.cell-value")
                        
                        student_name = None
                        
                        for span in value_spans:
                            text = span.text.strip()
                            if ',' in text and text.upper() != 'NO DATA':
                                student_name = text
                                break

                        if student_name:
                            print(f"SUCCESS - {i}: {student_name}")
                            c.execute("INSERT INTO students (id, name) VALUES (?, ?)", (i, student_name))
                            conn.commit()
                        else:
                            all_texts = [span.text.strip() for span in value_spans]
                            print(f"Ignoring ID {i}: No valid name found among results: {all_texts}")

                    except TimeoutException:
                        print(f"Ignoring ID {i}: No result elements found. Likely not a current student.")

                except Exception as e:
                    print(f"An unhandled error occurred for ID {i}: {e}")

    conn.close()

if __name__ == "__main__":
    main()
