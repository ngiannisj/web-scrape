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
urlExisting = "https://dhs.sa.gov.au/how-we-help/grants/available-grants"
urlUpcoming = "https://dhs.sa.gov.au/how-we-help/grants/future-grants"

# Send a GET request to the current grants rss feed
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
}
responseExisting = requests.get(urlExisting, headers=headers)
responseUpcoming = requests.get(urlUpcoming, headers=headers)


# Get all links for current grants from the XML content
if responseExisting.status_code == 200:
    html_content = responseExisting.content
    soup = BeautifulSoup(html_content, "html.parser")
    resultCardHtml = soup.find_all("div", class_="dhs-card__content")

# Get array of grant details from existing grant
grantListArr = []
for resultCard in resultCardHtml:
    grantDetailsObj = {}
    linkElement = resultCard.find("a", href=True)
    link = linkElement.get('href') if linkElement else "N/A"
    title = linkElement.get_text(strip=True) if linkElement else "N/A"
    description = resultCard.find("p", class_="dhs-card__copy").get_text(strip=True) if resultCard.find("p", class_="dhs-card__copy") else "N/A"

    # Populate grantDetailsObj
    grantDetailsObj["link"] = link
    grantDetailsObj["title"] = title
    grantDetailsObj["description"] = description
    grantDetailsObj["added_to_mongo_at"] = datetime.now(timezone.utc).isoformat()
    grantListArr.append(grantDetailsObj)

# Raise error and stop execution if no grants found
if not grantListArr:  # True if list is empty
    raise ValueError("No grants found on the webpage. The webpage structure may have changed.")

# Get all links for upcoming grants
if responseUpcoming.status_code == 200:
    upcoming_html_content = responseUpcoming.content
    upcomingSoup = BeautifulSoup(upcoming_html_content, "html.parser")
    upcomingResultContainer = upcomingSoup.find("div", id="component_170304")
    upcomingResults = upcomingResultContainer.find_all("h2") if upcomingResultContainer else []

# Get array of grant details from upcoming grants
for upcoming in upcomingResults:
    grantUpcomingDetailsObj = {}
    title = upcoming.get_text(strip=True)

    # Populate grantUpcomingDetailsObj
    grantUpcomingDetailsObj["link"] = "https://dhs.sa.gov.au/how-we-help/grants/future-grants"
    grantUpcomingDetailsObj["title"] = title
    grantUpcomingDetailsObj["added_to_mongo_at"] = datetime.now(timezone.utc).isoformat()
    grantListArr.append(grantUpcomingDetailsObj)

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
collection = db["sa_human_services"]  # You can change the collection name if you want

# Ensure unique index on 'title'
collection.create_index("title", unique=True)

if grantListArr:
    updated_count = 0
    inserted_count = 0
    for grant in grantListArr:
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
