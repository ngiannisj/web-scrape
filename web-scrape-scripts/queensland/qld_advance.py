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

# Define the URL api endpoint for current grants
url = "https://advance.qld.gov.au/grants-and-programs?external-uuid=2b1c5bf5-ecd4-4cac-97f9-6f9854a0d525&SQ_ASSET_CONTENTS_RAW&eventsroot=1851047&extrafilters=[%221867627%22,%221949150%22,%221949151%22]&extraprops=[%221867627%22,%221949150%22]&eventsfrom=anytime"
response = requests.get(url)
content_str = response.content.decode('utf-8')
data = json.loads(content_str)

grantsListArr = data.get("items", [])

for fields in grantsListArr:
    # Add timestamp for when entry is added
    fields['added_to_mongo_at'] = datetime.now(timezone.utc).isoformat()
    fields['title'] = fields['name'] if 'name' in fields else None
    fields['link'] = fields['url'] if 'url' in fields else None
    fields.pop("metadata", None)
    fields.pop("status_color", None)
    fields.pop("show_props", None)

# Keep only objects where status == "Live"
filtered_grants = [obj for obj in grantsListArr if obj.get("status") == "Live"]

# Insert grant details into MongoDB
db = client["grants_db"]
collection = db["qld_advance"]

# Ensure unique index on 'title'
collection.create_index("title", unique=True)

if filtered_grants:
    updated_count = 0
    inserted_count = 0
    for grant in filtered_grants:
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