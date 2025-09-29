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
url = "https://nt.gov.au/industry/business-grants-funding"

# Send a GET request to the current grants rss feed
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1"
}
response = requests.get(url, headers=headers)

# Get all links for current grants from the XML content
if response.status_code == 200:
    html_content = response.content
    soup = BeautifulSoup(html_content, "html.parser")
    resultCardHtml = soup.find_all("div", class_="card-body")

# Get array of grant details from each link
grantListArr = []
for resultCard in resultCardHtml:
    grantDetailsObj = {}
    status = resultCard.find("span", class_="grant-label-status").get_text(strip=True) if resultCard.find("span", class_="grant-label-status") else "N/A"
    link = resultCard.find("a", href=True).get('href') if resultCard.find("a", href=True) else "N/A"
    title = resultCard.find("h3", class_="grant-label-title").get_text(strip=True) if resultCard.find("h3", class_="grant-label-title") else "N/A"
    description = resultCard.find("p", class_="grant-label-description").get_text(strip=True) if resultCard.find("p", class_="grant-label-description") else "N/A"

    # Populate grantDetailsObj
    grantDetailsObj["status"] = status
    grantDetailsObj["link"] = link
    grantDetailsObj["title"] = title
    grantDetailsObj["description"] = description
    grantDetailsObj["added_to_mongo_at"] = datetime.now(timezone.utc).isoformat()
    grantListArr.append(grantDetailsObj)

# Raise error and stop execution if no grants found
if not grantListArr:  # True if list is empty
    raise ValueError("No grants found on the webpage. The webpage structure may have changed.")

# Filter out grants with status containing 'closed' (case insensitive)
filtered_arr = [obj for obj in grantListArr if obj.get("status") != "Closed"]

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
collection = db["nt_business"]  # You can change the collection name if you want

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
