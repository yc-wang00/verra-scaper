# ───────────────────────────────────────────────────── imports ────────────────────────────────────────────────────── #

import time

import pandas as pd
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from conf_mgr import conf_mgr

# Set options to run Chrome in headless mode
options = webdriver.ChromeOptions()
options.add_argument("headless")

# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #
#                                               Web Scrapper Main Script                                               #
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #

df = pd.read_excel(conf_mgr.path_data / "allprojects.xlsx", sheet_name="Results")

count = 0

# Iterate over the ID and Name columns
for id, name in zip(df["ID"], df["Name"]):

    logger.info(f"====================Counter: {count}====================")
    logger.info(f"Scraping <{name}> with ID {id}")

    url = f"https://registry.verra.org/app/projectDetail/VCS/{id}"

    # Set up the Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Open the page
    driver.get(url)

    try:
        # Wait for the element to load
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "card-text")))

        # Scrape the contents of the element
        raw_content = element.get_attribute("innerHTML")

        logger.debug(f"raw_content: {raw_content}")

        # Save the contents to a text file with name as the project id
        with open(conf_mgr.path_results / f"{id}.txt", "w") as f:
            f.write(raw_content)
    except Exception as e:
        logger.error(f"Failed to scrape {name} with ID {id}. Error: {e}")
    finally:
        driver.quit()

    logger.info(f"Finished scraping <{name}> with ID {id}")

    # Wait for 3 seconds before scraping the next project
    time.sleep(5)

    count += 1

    ### Uncomment the following line to scrape project by number ###
    # if count == 1:
    #     break
