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
    try:
        result = collection.insert_many(fields_array, ordered=False)
        print(f"Inserted {len(result.inserted_ids)} new grants into MongoDB.")
    except BulkWriteError as bwe:
        inserted = bwe.details.get('nInserted', 0)
        print(f"Inserted {inserted} new grants. Some were duplicates and skipped.")
else:
    print("No grants found to insert.")