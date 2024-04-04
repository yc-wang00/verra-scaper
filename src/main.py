"""
This script serves as the main entry point for the web scrapper. It scrapes the project details from the Verra registry.
"""

# ───────────────────────────────────────────────────── imports ────────────────────────────────────────────────────── #

import time
import csv
import argparse

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


def main(scrape_summary=True, scrape_document_links=True) -> None:
    """
    Main function to scrape project details from the Verra registry.

    Args:
        scrape_summary (bool): Flag to indicate whether to scrape project summary content. Default is True.
        scrape_document_links (bool): Flag to indicate whether to scrape project document links. Default is True.
    """

    # Load the Excel file with the project IDs and Names
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
            # Scrape the summary content
            if scrape_summary:
                # Wait for the element to load
                element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "card-text")))

                # Scrape the contents of the element
                raw_content = element.get_attribute("innerHTML")

                logger.debug(f"raw_content: {raw_content}")

                # Save the contents to a text file with name as the project id
                with open(conf_mgr.path_results / f"{id}.txt", "w") as f:
                    f.write(raw_content)

            # Scrape the document links
            if scrape_document_links:

                document_headers = [
                    "VCS Registration Documents",
                    "VCS Pipeline Documents",
                    "VCS Issuance Documents",
                    "VCS Other Documents",
                ]

                document_groups = []
                for header in document_headers:
                    # Find the document group by its unique header
                    found_document_group = driver.find_elements(
                        By.XPATH,
                        f"//div[contains(@class,'card') and .//div[contains(@class,'card-header')][contains(text(),'{header}')]]",
                    )

                    # Check that only one document group was found
                    assert (
                        len(found_document_group) == 1
                    ), f"Expected 1 document group for header {header}, but found {len(found_document_group)}"

                    # Append the found document group to the list
                    document_groups.append(found_document_group[0])

                for group_name, group in zip(document_headers, document_groups):
                    # Extract the PDF links, names, and dates within each group
                    pdf_links = group.find_elements(By.CSS_SELECTOR, "table tbody tr td a")
                    dates = group.find_elements(By.CSS_SELECTOR, "table tbody tr td:nth-child(2)")

                    for link, date in zip(pdf_links, dates):
                        pdf_url = link.get_attribute("href")
                        pdf_name = link.text
                        date_updated = date.text

                        # Write the PDF link to a CSV file
                        with open("pdf_links.csv", mode="a", newline="", encoding="utf-8") as file:
                            writer = csv.writer(file)
                            writer.writerow([id, group_name, pdf_name, pdf_url, date_updated])

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web Scrapper")
    parser.add_argument(
        "-ds", "--disable-summary", dest="disable_summary", action="store_true", help="No scraping of the summary"
    )
    parser.add_argument(
        "-dd",
        "--disable-document",
        dest="disable_document",
        action="store_true",
        help="No scraping of the document links",
    )
    args = parser.parse_args()
    if args.disable_summary and args.disable_document:
        logger.error("Both summary and document scraping are disabled. Exiting...")
        exit(1)
    breakpoint()

    # Create the CSV file to store the PDF links
    with open("pdf_links.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(["Project ID", "Document Type", "Document Name", "Document URL", "Date Updated"])

    # if args.summary_only:
    #     logger.info("Scraping only the summary")
    #     scrape_summary()
    # elif args.document_only:
    #     logger.info("Scraping only the document links")
    #     scrape_document_links()
    # else:
