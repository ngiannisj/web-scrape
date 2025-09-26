import requests
from bs4 import BeautifulSoup
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import BulkWriteError
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import re
import json

# Load environment variables from .env file
load_dotenv()
mongoUri = os.getenv("MONGO_URI")
client = MongoClient(mongoUri, server_api=ServerApi('1'))

# Define the URL of the webpage to scrape
url = "https://business.vic.gov.au/grants-and-programs"

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
    script_tag = soup.find("script", string=re.compile("grantsData"))

grantListArr = []
if script_tag:
    script_content = script_tag.get_text(strip=True, separator="")
    grants_json = script_content.replace("var grantsData = ", "").strip().rstrip(";")
    grants_json  = re.sub(r"[\r\n]+", "", grants_json)

    # 1. Remove comments like /* ... */
    grants_json = re.sub(r"/\*.*?\*/", "", grants_json , flags=re.S)

    # 2. Remove trailing commas before ] or }
    grants_json = re.sub(r",(\s*[\]}])", r"\1", grants_json)
    grantListArr = json.loads(grants_json)

for grant in grantListArr:
    grant['link'] = grant['targetURL'] if 'targetURL' in grant else None
    grant["added_to_mongo_at"] = datetime.now(timezone.utc).isoformat()

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
collection = db["vic_business"]  # You can change the collection name if you want

# Ensure unique index on 'title'
collection.create_index("title", unique=True)

if grantListArr:
    try:
        result = collection.insert_many(grantListArr, ordered=False)
        print(f"Inserted {len(result.inserted_ids)} new grants into MongoDB.")
    except BulkWriteError as bwe:
        inserted = bwe.details.get('nInserted', 0)
        print(f"Inserted {inserted} new grants. Some were duplicates and skipped.")
else:
    print("No grants found to insert.")