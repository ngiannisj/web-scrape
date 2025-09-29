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

url = "https://www.vic.gov.au/api/tide/app-search/content-vic-production/elasticsearch/_search"

payload = {
    "query": {
        "function_score": {
            "query": {
                "bool": {
                    "must": [{"match_all": {}}],
                    "filter": [
                        {"terms": {"type": ["grant"]}},
                        {"terms": {"field_node_site": [4]}},
                        {
                            "bool": {
                                "should": [
                                    {
                                        "bool": {
                                            "must": [
                                                {
                                                    "range": {
                                                        "field_node_dates_start_value": {
                                                            "lte": "now"
                                                        }
                                                    }
                                                },
                                                {
                                                    "range": {
                                                        "field_node_dates_end_value": {
                                                            "gte": "now"
                                                        }
                                                    }
                                                },
                                            ],
                                            "must_not": [
                                                {
                                                    "term": {
                                                        "field_node_on_going": "true"
                                                    }
                                                }
                                            ],
                                        }
                                    },
                                    {"term": {"field_node_on_going": "true"}},
                                    {
                                        "range": {
                                            "field_node_dates_start_value": {
                                                "gte": "now"
                                            }
                                        }
                                    },
                                ]
                            }
                        },
                    ],
                }
            },
            "functions": [
                {
                    "filter": {
                        "bool": {
                            "must": [
                                {
                                    "range": {
                                        "field_node_dates_start_value": {"lte": "now"}
                                    }
                                },
                                {
                                    "range": {
                                        "field_node_dates_end_value": {"gte": "now"}
                                    }
                                },
                                {"term": {"field_node_on_going": False}},
                            ]
                        }
                    },
                    "weight": 4,
                },
                {
                    "filter": {
                        "bool": {
                            "must": [
                                {
                                    "range": {
                                        "field_node_dates_start_value": {"lte": "now"}
                                    }
                                },
                                {
                                    "range": {
                                        "field_node_dates_end_value": {"gte": "now"}
                                    }
                                },
                            ],
                            "must_not": [{"exists": {"field": "field_node_on_going"}}],
                        }
                    },
                    "weight": 4,
                },
                {"filter": [{"term": {"field_node_on_going": True}}], "weight": 3},
                {
                    "filter": [{"range": {"field_node_dates_start_value": {"gte": "now"}}}],
                    "weight": 2,
                },
            ],
            "score_mode": "sum",
            "boost_mode": "multiply",
        }
    },
    "size": 1000,
    "from": 0,
    "sort": [
        {"_score": "desc"},
        {"field_node_dates_end_value": "asc"},
        {"title.keyword": "asc"},
    ],
}
response = requests.post(url, json=payload)
content_str = response.content.decode('utf-8')
data = json.loads(content_str)

fields_array = [hit['_source'] for hit in data['hits']['hits']]

# Raise error and stop execution if no grants found
if not fields_array:  # True if list is empty
    raise ValueError("No grants found on the webpage. The webpage structure may have changed.")

for fields in fields_array:
    # Add timestamp for when entry is added
    fields['added_to_mongo_at'] = datetime.now(timezone.utc).isoformat()
    fields['link'] = "https://www.vic.gov.au" + fields['url'][0] if 'url' in fields else None

# Insert grant details into MongoDB
db = client["grants_db"]
collection = db["vic_grants"]


# Ensure unique index on 'title'
collection.create_index("title", unique=True)

if fields_array:
    updated_count = 0
    inserted_count = 0
    for grant in fields_array:
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