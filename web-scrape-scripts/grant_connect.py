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
url = "https://www.grants.gov.au/public_data/rss/rss.xml"

# Send a GET request to the current grants rss feed
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
}
response = requests.get(url, headers=headers)

# Get all links for current grants from the XML content
sanitizedUrlArr = []
if response.status_code == 200:
    xml_content = response.content
    soup = BeautifulSoup(xml_content, "xml")
    urlTagArr = soup.find_all("link")
    for url in urlTagArr:
        sanitizedUrlArr.append(url.text.strip())

# Get array of grant details from each link
grantListArr = []
if len(sanitizedUrlArr) > 0:
    for link in sanitizedUrlArr:
        grantDetailsObj = {}
        if link.startswith("https://www.grants.gov.au/Go/Show?"):
            # Get grant id from the link
            grantId = link.split("GoUuid=")[-1]
            grantResponse = requests.get(link, headers=headers)
            if grantResponse.status_code == 200:
                # Get grant details
                grantSoup = BeautifulSoup(grantResponse.content, "html.parser")
                titleDiv = grantSoup.find('p', attrs={'class': 'font20', 'role': 'heading'})
                detailDivArr = grantSoup.find_all("div", class_="list-desc")
                for detailDiv in detailDivArr:
                    grantDetailTitle = detailDiv.find("span").get_text()
                    grantDetailDescription = detailDiv.find("div", class_="list-desc-inner").get_text(strip=True, separator=" ")
                    grantDetailsObj[grantDetailTitle] = grantDetailDescription
                grantDetailsObj["added_to_mongo_at"] = datetime.now(timezone.utc).isoformat()
                grantDetailsObj["title"] = titleDiv.get_text(strip=True, separator=" ")
                grantDetailsObj["link"] = link
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
collection = db["grant_connect"]  # You can change the collection name if you want

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
