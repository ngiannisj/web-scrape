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

# Raise error and stop execution if no grants found
if not data.items():  # True if list is empty
    raise ValueError("No grants found on the webpage. The webpage structure may have changed.")

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
    updated_count = 0
    inserted_count = 0
    for grant in filtered_list:
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
