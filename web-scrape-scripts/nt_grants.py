import requests
import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import BulkWriteError
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import re

# Load environment variables from .env file
load_dotenv()
mongoUri = os.getenv("MONGO_URI")
client = MongoClient(mongoUri, server_api=ServerApi('1'))

url = "https://grantsnt.nt.gov.au/api/v1/grants/search"

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "clientversion": "3.1.0.77",
    "content-type": "application/json",
    "referer": "https://grantsnt.nt.gov.au/grants"
}

payload = {
    "agencies": [],
    "categories": [],
    "beneficiaries": [],
    "publicContentTypes": [],
    "pageSize": 10000,
    "page": 1,
    "sortColumn": "PublishDateFrom",
    "sortDirection": 2,
    "contentSlug": ""
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
content_str = response.content.decode('utf-8')
data = json.loads(content_str)
grantListArr = data['results']


for grant in grantListArr:
    grant['link'] = "https://grantsnt.nt.gov.au/grants/"
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
collection = db["nt_grants"]  # You can change the collection name if you want

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