import requests
import json
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

url = "https://api.jus-checklist.services.qld.gov.au/v1/api/legacy/resources/grants/services.json?"

headers = {
    "x-api-key": "sfxLO52gBA65yVOkxkkqX5qjK2EvvaNx3iARcf2y",
}

response = requests.get(url, headers=headers)
content_str = response.content.decode('utf-8')
data = json.loads(content_str)

def flatten_details(entry: dict) -> dict:
    """Flatten the 'details' object into key:value pairs."""
    details = entry.get("details", {})
    flat = {}
    for key, val in details.items():
        if isinstance(val, dict) and "sections" in val:
            flat[key] = val["sections"][0].get("data", "") if val["sections"] else ""
        else:
            flat[key] = ""
    return flat


def flatten_all_to_list_filtered(data: dict) -> list[dict]:
    """Flatten details for all records, filter out those with status 'Closed'."""
    flattened = []
    for rec_id, rec in data.items():
        flat_details = flatten_details(rec)
        new_entry = {k: v for k, v in rec.items() if k != "details"}
        new_entry.update(flat_details)
        # Only include if status is not 'Closed'
        if new_entry.get("status", "").lower() != "closed":
            flattened.append(new_entry)
    return flattened

filtered_list = flatten_all_to_list_filtered(data)

for fields in filtered_list:
    # Add timestamp for when entry is added
    fields['added_to_mongo_at'] = datetime.now(timezone.utc).isoformat()
    fields['title'] = fields['name'] if 'name' in fields else None
    fields['link'] = "https://www.grants.services.qld.gov.au/service-details/" + fields['id'] if 'id' in fields else None

# Insert grant details into MongoDB
db = client["grants_db"]
collection = db["qld_grants"]

# Ensure unique index on 'title'
collection.create_index("title", unique=True)

if filtered_list:
    try:
        result = collection.insert_many(filtered_list, ordered=False)
        print(f"Inserted {len(result.inserted_ids)} new grants into MongoDB.")
    except BulkWriteError as bwe:
        inserted = bwe.details.get('nInserted', 0)
        print(f"Inserted {inserted} new grants. Some were duplicates and skipped.")
else:
    print("No grants found to insert.")