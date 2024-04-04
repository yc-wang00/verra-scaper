"""
This file will be used to clean the data scraped from the website. 

This is a backup of the code that runs in the jupyter notebook. The code in the jupyter notebook is more interactive and easier to debug.
"""

import pandas as pd
from bs4 import BeautifulSoup
import json
import weaviate


# ──────────────────────────────────────────────── Clean scraped data ──────────────────────────────────────────────── #

df = pd.read_excel("data/registered.xlsx", sheet_name="Results")

# Convert Timestamps to strings in datetime columns
datetime_columns = df.select_dtypes(include=["datetime"]).columns
df[datetime_columns] = df[datetime_columns].apply(lambda x: x.dt.strftime("%Y-%m-%d") if not pd.isnull(x).all() else x)
df = df.where(pd.notnull(df), None)


"""['ID', 'Name', 'Proponent', 'Project Type', 'AFOLU Activities',
    'Methodology', 'Status', 'Country/Area',
    'Estimated Annual Emission Reductions', 'Region',
    'Project Registration Date', 'Crediting Period Start Date',
    'Crediting Period End Date'
"""

df.rename(
    columns={
        "ID": "project_id",
        "Name": "name",
        "Proponent": "proponent",
        "Project Type": "project_type",
        "AFOLU Activities": "afolu_activities",
        "Methodology": "methodology",
        "Status": "status",
        "Country/Area": "country_area",
        "Estimated Annual Emission Reductions": "estimated_annual_emission_reductions",
        "Region": "region",
        "Project Registration Date": "project_registration_date",
        "Crediting Period Start Date": "crediting_period_start_date",
        "Crediting Period End Date": "crediting_period_end_date",
    },
    inplace=True,
)


# ──────────────────────────────────────────────── Convert into json ───────────────────────────────────────────────── #


def extract_text(html_string):
    # Parse the HTML content
    soup = BeautifulSoup(html_string, "html.parser")

    # Extract text from parsed HTML
    return soup.get_text()


json_output = {}

# iterate over two columns, id and name zip them
for json_object in df.to_dict("records"):
    id = json_object["project_id"]
    name = json_object["name"]
    try:
        with open(f"data/registered/{id}.txt", "r", encoding="utf-8") as file:
            html_content = file.read()
        # Extracting the text
        extracted_text = extract_text(html_content)
        json_object["text"] = extracted_text
    except Exception:
        print(f"Error with {id}")
        continue
    json_output[id] = json_object

with open("data/clean_registered.json", "w") as fp:
    json.dump(json_output, fp, indent=4, sort_keys=True)


# ─────────────────────────────────────────── Import data into weaviate DB ─────────────────────────────────────────── #

breakpoint()

# Replace with your Weaviate instance URL
WEAVIATE_URL = "http://localhost:8080"


def setup_weaviate_connection():
    """Setup the connection to the Weaviate instance"""
    client = weaviate.Client(url=WEAVIATE_URL)
    return client


def import_data_to_weaviate(client, data):
    """Import the prepared data into Weaviate"""
    for obj in data:
        try:
            client.data_object.create(data_object=obj, class_name="Registed_Metadata")
        except Exception as e:
            print(f"Error importing object with ID {obj['project_id']}: {str(e)}")


client = setup_weaviate_connection()
import_data_to_weaviate(client, json_output.values())
