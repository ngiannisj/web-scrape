import requests
from bs4 import BeautifulSoup
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import BulkWriteError
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
mongoUri = os.getenv("MONGO_URI")
client = MongoClient(mongoUri, server_api=ServerApi('1'))

# Define the URL of the webpage to scrape
url = "https://www.act.gov.au/money-and-tax/grants-funding-and-incentives"

# Send a GET request to the current grants rss feed
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
}
response = requests.get(url, headers=headers)

# Get all links for current grants from the XML content
sanitizedUrlArr = []
if response.status_code == 200:
    html_content = response.content
    soup = BeautifulSoup(html_content, "html.parser")
    resultCardHtml = soup.find_all("div", class_="result")

# Get array of grant details from each link
grantListArr = []
for resultCard in resultCardHtml:
    grantDetailsObj = {}
    status = resultCard.find("span", class_="status").get_text(strip=True) if resultCard.find("span", class_="status") else "N/A"
    link = resultCard.find("a", href=True).get('href') if resultCard.find("a", href=True) else "N/A"
    title = resultCard.find("p", class_="act-grant-subtitle").get_text(strip=True) if resultCard.find("p", class_="act-grant-subtitle") else "N/A"
    description = resultCard.find("div", class_="act-search-result__body").find("p").get_text(strip=True) if resultCard.find("div", class_="act-search-result__body").find("p") else "N/A"
    amount = resultCard.find("span", class_="funding-amount").get_text(strip=True) if resultCard.find("span", class_="funding-amount") else "N/A"
    who_can_apply = resultCard.find("span", class_="who-can-apply").get_text(strip=True) if resultCard.find("span", class_="who-can-apply") else "N/A"
    tags = resultCard.find("div", attrs={'class': 'act-tag__container', 'style': 'margin-top: 16px;'}).get_text(strip=True, separator=", ") if resultCard.find("div", attrs={'class': 'act-tag__container', 'style': 'margin-top: 16px;'}) else "N/A"

    # Populate grantDetailsObj
    grantDetailsObj["status"] = status
    grantDetailsObj["link"] = link
    grantDetailsObj["title"] = title
    grantDetailsObj["description"] = description
    grantDetailsObj["amount"] = amount
    grantDetailsObj["who_can_apply"] = who_can_apply
    grantDetailsObj["tags"] = tags
    grantDetailsObj["added_to_mongo_at"] = datetime.now(timezone.utc).isoformat()
    grantListArr.append(grantDetailsObj)

# Filter out grants with status containing 'closed'
filtered_arr = [
    grant for grant in grantListArr
    if "closed" not in grant.get("status", "").lower()
]

# Get a list of all property names in grantListArr objects
property_names = set()
for grant in grantListArr:
    property_names.update(grant.keys())
property_names = list(property_names)

# Move 'title' to the front if it exists
if 'title' in property_names:
    property_names.remove('title')
    property_names.insert(0, 'title')

# Insert grant details into MongoDB
db = client["grants_db"]  # You can change the database name if you want
collection = db["act_grants"]  # You can change the collection name if you want

# Ensure unique index on 'title'
collection.create_index("title", unique=True)

if filtered_arr:
    updated_count = 0
    inserted_count = 0
    for grant in filtered_arr:
        # Extract added_to_mongo_at separately so we can use $setOnInsert
        added_at = grant.get("added_to_mongo_at")
        grant_no_added_at = {k: v for k, v in grant.items() if k != "added_to_mongo_at"}

        result = collection.update_one(
            {"title": grant["title"]},   # Match by title
            {
                "$set": {
                    **grant_no_added_at,
                    "last_updated_at": datetime.now(timezone.utc).isoformat()
                },
                "$setOnInsert": {"added_to_mongo_at": added_at}
            },
            upsert=True
        )

        if result.matched_count > 0:
            if result.modified_count > 0:
                updated_count += 1
        elif result.upserted_id is not None:
            inserted_count += 1

    print(f"Inserted {inserted_count} new grants, updated {updated_count} existing grants.")
else:
    print("No grants found to insert or update.")
