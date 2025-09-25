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
url = "https://www.nsw.gov.au/api/v1/elasticsearch/prod_content/_search?source_content_type=application%2Fjson&source=%7B%22_source%22%3Afalse%2C%22from%22%3A0%2C%22size%22%3A10000%2C%22sort%22%3A%5B%22subtype_index%22%2C%7B%22grant_is_ongoing%22%3A%22desc%22%7D%2C%7B%22grant_date_range_sort.lte%22%3A%7B%22order%22%3A%22asc%22%2C%22mode%22%3A%22min%22%2C%22nested%22%3A%7B%22path%22%3A%22grant_date_range_sort%22%2C%22filter%22%3A%7B%22bool%22%3A%7B%22must%22%3A%5B%7B%22range%22%3A%7B%22grant_date_range_sort.lte%22%3A%7B%22gte%22%3A1756004769375%7D%7D%7D%2C%7B%22range%22%3A%7B%22grant_date_range_sort.gte%22%3A%7B%22lte%22%3A1756004769375%7D%7D%7D%5D%7D%7D%7D%2C%22missing%22%3A%22_last%22%7D%7D%2C%7B%22grant_date_range_sort.gte%22%3A%7B%22order%22%3A%22asc%22%2C%22mode%22%3A%22min%22%2C%22nested%22%3A%7B%22path%22%3A%22grant_date_range_sort%22%2C%22filter%22%3A%7B%22range%22%3A%7B%22grant_date_range_sort.gte%22%3A%7B%22gte%22%3A1756004769375%7D%7D%7D%7D%2C%22missing%22%3A%22_last%22%7D%7D%5D%2C%22query%22%3A%7B%22bool%22%3A%7B%22_name%22%3A%22first_pass%22%2C%22must%22%3A%5B%7B%22bool%22%3A%7B%22minimum_should_match%22%3A1%2C%22should%22%3A%7B%22term%22%3A%7B%22grant_date_range%22%3A1756004769375%7D%7D%7D%7D%2C%7B%22match_all%22%3A%7B%22boost%22%3A2%7D%7D%5D%2C%22filter%22%3A%5B%7B%22term%22%3A%7B%22type%22%3A%22grant%22%7D%7D%2C%7B%22term%22%3A%7B%22status%22%3A%22true%22%7D%7D%5D%7D%7D%2C%22fields%22%3A%5B%22title%22%2C%22subtype%22%2C%22status%22%2C%22url%22%2C%22field_summary%22%2C%22hero_media_id%22%2C%22grant_amount%22%2C%22grant_amount_max%22%2C%22grant_amount_min%22%2C%22grant_is_ongoing%22%2C%22grant_fund%22%2C%7B%22field%22%3A%22grant_date_range%22%2C%22format%22%3A%22epoch_millis%22%7D%2C%22grant_audience%22%2C%22grant_amount_text%22%2C%22grant_amount_single%2C%22%5D%7D"

response = requests.get(url)
content_str = response.content.decode('utf-8')
data = json.loads(content_str)

fields_array = [hit['fields'] for hit in data['hits']['hits']]

for fields in fields_array:
    # Convert epoch milliseconds to human-readable date format for grant_date_range
    if 'grant_date_range' in fields:
        for i in range(len(fields['grant_date_range'])):
            gteMilliseconds = fields['grant_date_range'][i]['gte'] if 'gte' in fields['grant_date_range'][i] else None
            if gteMilliseconds is not None:
                if isinstance(gteMilliseconds, str):
                    gteMilliseconds = int(gteMilliseconds)
                seconds = gteMilliseconds / 1000
                fields['grant_date_range'][i]['startDate'] = datetime.fromtimestamp(seconds).strftime("%d/%m/%Y")
                del fields['grant_date_range'][i]['gte']
            
            lteMilliseconds = fields['grant_date_range'][i]['lte'] if 'lte' in fields['grant_date_range'][i] else None
            if lteMilliseconds is not None:
                if isinstance(lteMilliseconds, str):
                    lteMilliseconds = int(lteMilliseconds)
                seconds = lteMilliseconds / 1000
                fields['grant_date_range'][i]['endDate'] = datetime.fromtimestamp(seconds).strftime("%d/%m/%Y")
                del fields['grant_date_range'][i]['lte']

    # Remove hero_media_id field as it is not needed
    if 'hero_media_id' in fields:
        del fields['hero_media_id']

    # Add timestamp for when entry is added
    fields['added_to_mongo_at'] = datetime.now(timezone.utc).isoformat()

# Insert grant details into MongoDB
db = client["grants_db"]
collection = db["nsw_grants"]

# Ensure unique index on 'title'
collection.create_index("title", unique=True)

if fields_array:
    try:
        result = collection.insert_many(fields_array, ordered=False)
        print(f"Inserted {len(result.inserted_ids)} new grants into MongoDB.")
    except BulkWriteError as bwe:
        inserted = bwe.details.get('nInserted', 0)
        print(f"Inserted {inserted} new grants. Some were duplicates and skipped.")
else:
    print("No grants found to insert.")