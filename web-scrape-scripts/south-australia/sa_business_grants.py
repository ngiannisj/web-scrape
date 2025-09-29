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
urlGrants = "https://business.sa.gov.au/programs/grant-programs"
urlPrograms = "https://business.sa.gov.au/programs"


# Send a GET request to the current grants rss feed
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
}
responseGrants = requests.get(urlGrants, headers=headers)
responsePrograms = requests.get(urlPrograms, headers=headers)


# Get all links for current grants from the XML content
if responseGrants.status_code == 200:
    html_content_grants = responseGrants.content
    soupGrants = BeautifulSoup(html_content_grants, "html.parser")
    resultCardsGrants = soupGrants.select(".col-span-1.pb-4")

# Get array of grant details from each link
grantListArr = []
for resultCard in resultCardsGrants:
    grantDetailsObj = {}
    link = resultCard.find("a", href=True).get('href') if resultCard.find("a", href=True) else "N/A"
    title = resultCard.select(".t-copy-large.mb-6")[0].get_text(strip=True) if resultCard.select(".t-copy-large.mb-6") else "N/A"
    description = resultCard.select(".t-copy.mb-6")[0].get_text(strip=True)

    # Populate grantDetailsObj
    grantDetailsObj["link"] = link
    grantDetailsObj["title"] = title
    grantDetailsObj["description"] = description
    grantDetailsObj["added_to_mongo_at"] = datetime.now(timezone.utc).isoformat()
    grantListArr.append(grantDetailsObj)

# Raise error and stop execution if no grants found
if not grantListArr:  # True if list is empty
    raise ValueError("No grants found on the webpage. The webpage structure may have changed.")

    # Get all links for current grants from the XML content
if responsePrograms.status_code == 200:
    html_content_programs = responsePrograms.content
    soupPrograms = BeautifulSoup(html_content_programs, "html.parser")
    resultCardsPrograms = soupPrograms.select(".grid.gap-default.h-full")

# Get array of grant details from each link
for resultCard in resultCardsPrograms:
    grantDetailsObj = {}
    linkProgram = resultCard.find("a", href=True).get('href') if resultCard.find("a", href=True) else "N/A"
    titleProgram = resultCard.select(".t-subheading.mb-6")[0].get_text(strip=True) if resultCard.select(".t-subheading.mb-6") else "N/A"
    descriptionProgram = resultCard.select(".t-copy.mb-6")[0].get_text(strip=True)

    # Populate grantDetailsObj
    grantDetailsObj["link"] = linkProgram
    grantDetailsObj["title"] = titleProgram
    grantDetailsObj["description"] = descriptionProgram
    grantDetailsObj["added_to_mongo_at"] = datetime.now(timezone.utc).isoformat()
    grantListArr.append(grantDetailsObj)

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
collection = db["sa_business"]  # You can change the collection name if you want

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
