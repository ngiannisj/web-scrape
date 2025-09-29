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

url = "https://departmentofindustryscienceenergyandresourcesproduxlo9oz8e.org.coveo.com/rest/search/v2?organizationId=departmentofindustryscienceenergyandresourcesproduxlo9oz8e"

headers = {
    "authorization": "Bearer xx9eeaa647-9038-418e-b985-9a469f276965",
    "content-type": "application/json",
}

payload = {
    "locale": "en-US",
    "debug": False,
    "tab": "default",
    "referrer": "https://business.gov.au/",
    "timezone": "Australia/Sydney",
    "cq": "(NOT @z95xtemplate==(ADB6CA4F03EF4F47B9AC9CE2BA53FF97,FE5DD82648C6436DB87A7C4210C7413B)) "
          "((@z95xtemplate==64642b7d33654d6aabfaa209fe642da9) (@ez120xcludez32xfromz32xsearch==0) "
          "OR @z95xtemplate==03c2e6e6631e4ba9b889e4455d7eb090) (@z95xlanguage==en) (@z95xlatestversion==1) "
          "(@source==\\\"Coveo_web_index - BGA Prod Environment\\\")",
    "context": {"fcq": ""},
    "fieldsToInclude": [
        "author","language","urihash","objecttype","collection","source","permanentid","z95xid","curl","ctitle","csa",
        "fsearchz32xandz32xheaderz32xdescription28333","cet","clabelortitle","z95xtemplate","fshortz32xdescription28333",
        "z95xtemplatename","cesdelivery","ceseventtype","cesbusinessstate","cestitle","cesdate","cesduration","cesloc",
        "cescost","cesspeakers","cesorganiser","cessponsors","cesaddress","registrationz32xwebsite","cesregister",
        "cesdescription","cescontent","cgs","labelz32xoverride","startz32xdate","closez32xdate",
        "nez120xtz32xgrantz32xinz32xsequence","noz32xstartz32xtime","noz32xclosez32xtime","whoz32xthisz32xisz32xfor",
        "whatz32xyouz32xget","fheading28333","cadelivery","cascdelivery","cacost","captype","caslatitude","caslongitude",
        "csearchcarddescription","canz122xsrccodestr","clocaddress","ccontactperson","ccontactphone","creferenceurl",
        "creferenceurllabel","rspz32xnumber","crspcat","registrationz32xvalidz32xto","abn"
    ],
    "q": "",
    "enableQuerySyntax": False,
    "searchHub": "Grants and programs",
    "sortCriteria": "@cgrantsort ascending",
    "analytics": {
        "clientId": "2e6e610e-43b9-475f-9125-b1362bf1fada",
        "clientTimestamp": "2025-09-27T02:57:55.746Z",
        "documentReferrer": "https://business.gov.au/",
        "documentLocation": "https://business.gov.au/grants-and-programs?cgs=fi131,fi132",
        "originContext": "Search",
        "actionCause": "facetDeselect",
        "capture": True,
        "source": ["@coveo/headless@3.22.1"],
    },
    "queryCorrection": {"enabled": True, "options": {"automaticallyCorrect": "whenNoResults"}},
    "enableDidYouMean": False,
    "facets": [
        {
            "filterFacetCount": True,
            "injectionDepth": 1000,
            "numberOfValues": 500,
            "sortCriteria": "automatic",
            "resultsMustMatch": "atLeastOneValue",
            "type": "specific",
            "currentValues": [
                {"value": "Australian Capital Territory","state": "idle"},
                {"value": "New South Wales","state": "idle"},
                {"value": "Northern Territory","state": "idle"},
                {"value": "Queensland","state": "idle"},
                {"value": "South Australia","state": "idle"},
                {"value": "Tasmania","state": "idle"},
                {"value": "Victoria","state": "idle"},
                {"value": "Western Australia","state": "idle"},
                {"value": "Other Australian territory","state": "idle"}
            ],
            "freezeCurrentValues": True,
            "isFieldExpanded": False,
            "preventAutoSelect": False,
            "field": "cloc",
            "facetId": "cloc",
            "tabs": {},
            "activeTab": ""
        },
        {
            "filterFacetCount": True,
            "injectionDepth": 1000,
            "numberOfValues": 500,
            "sortCriteria": "automatic",
            "resultsMustMatch": "atLeastOneValue",
            "type": "specific",
            "currentValues": [
                {"value": "Only show regional or rural area opportunities","state": "idle"}
            ],
            "freezeCurrentValues": True,
            "isFieldExpanded": False,
            "preventAutoSelect": False,
            "field": "crra",
            "facetId": "crra",
            "tabs": {},
            "activeTab": ""
        },
        {
            "filterFacetCount": True,
            "injectionDepth": 1000,
            "numberOfValues": 500,
            "sortCriteria": "automatic",
            "resultsMustMatch": "atLeastOneValue",
            "type": "specific",
            "currentValues": [
                {"value": "Accommodation and food services","state": "idle"},
                {"value": "Administrative and support services","state": "idle"},
                {"value": "Agriculture, forestry and fishing","state": "idle"},
                {"value": "Arts and recreation services","state": "idle"},
                {"value": "Construction","state": "idle"},
                {"value": "Defence","state": "idle"},
                {"value": "Education and training","state": "idle"},
                {"value": "Electricity, gas, water and waste services","state": "idle"},
                {"value": "Financial and insurance services","state": "idle"},
                {"value": "Health care and social assistance","state": "idle"},
                {"value": "Information media and telecommunications","state": "idle"},
                {"value": "Manufacturing","state": "idle"},
                {"value": "Mining","state": "idle"},
                {"value": "Professional, scientific and technical services","state": "idle"},
                {"value": "Public administration and safety","state": "idle"},
                {"value": "Rental, hiring and real estate services","state": "idle"},
                {"value": "Retail trade","state": "idle"},
                {"value": "Transport, postal and warehousing","state": "idle"},
                {"value": "Wholesale trade","state": "idle"},
                {"value": "Other services","state": "idle"}
            ],
            "freezeCurrentValues": True,
            "isFieldExpanded": False,
            "preventAutoSelect": False,
            "field": "cind",
            "facetId": "cind",
            "tabs": {},
            "activeTab": ""
        },
        {
            "filterFacetCount": True,
            "injectionDepth": 1000,
            "numberOfValues": 500,
            "sortCriteria": "automatic",
            "resultsMustMatch": "atLeastOneValue",
            "type": "specific",
            "currentValues": [
                {"value": "Exclude grants for all industries","state": "idle"}
            ],
            "freezeCurrentValues": True,
            "isFieldExpanded": False,
            "preventAutoSelect": False,
            "field": "caind",
            "facetId": "caind",
            "tabs": {},
            "activeTab": ""
        },
        {
            "filterFacetCount": True,
            "injectionDepth": 1000,
            "numberOfValues": 500,
            "sortCriteria": "automatic",
            "resultsMustMatch": "atLeastOneValue",
            "type": "specific",
            "currentValues": [
                {"value": "Company","state": "idle"},
                {"value": "Not for profit","state": "idle"},
                {"value": "Partnership","state": "idle"},
                {"value": "Sole trader","state": "idle"},
                {"value": "Trust","state": "idle"}
            ],
            "freezeCurrentValues": True,
            "isFieldExpanded": False,
            "preventAutoSelect": False,
            "field": "cbt",
            "facetId": "cbt",
            "tabs": {},
            "activeTab": ""
        },
        {
            "filterFacetCount": True,
            "injectionDepth": 1000,
            "numberOfValues": 500,
            "sortCriteria": "automatic",
            "resultsMustMatch": "atLeastOneValue",
            "type": "specific",
            "currentValues": [
                {"value": "Advice and mentoring","state": "idle"},
                {"value": "Funding","state": "idle"},
                {"value": "Loan","state": "idle"},
                {"value": "Sponsorship","state": "idle"},
                {"value": "Subsidies and rebates","state": "idle"},
                {"value": "Tax benefits","state": "idle"}
            ],
            "freezeCurrentValues": True,
            "isFieldExpanded": False,
            "preventAutoSelect": False,
            "field": "cst",
            "facetId": "cst",
            "tabs": {},
            "activeTab": ""
        },
        {
            "filterFacetCount": True,
            "injectionDepth": 1000,
            "numberOfValues": 500,
            "sortCriteria": "automatic",
            "resultsMustMatch": "atLeastOneValue",
            "type": "specific",
            "currentValues": [
                {"value": "Building improvements","state": "idle"},
                {"value": "Community or cultural heritage projects","state": "idle"},
                {"value": "Conduct research and development","state": "idle"},
                {"value": "Employing","state": "idle"},
                {"value": "Environmental management","state": "idle"},
                {"value": "Equipment, vehicles or tools","state": "idle"},
                {"value": "Importing or exporting","state": "idle"},
                {"value": "Investing money in other businesses","state": "idle"},
                {"value": "Manufacturing","state": "idle"},
                {"value": "Natural disasters or emergencies","state": "idle"},
                {"value": "Online and digital","state": "idle"},
                {"value": "Operational costs","state": "idle"},
                {"value": "Organising an event","state": "idle"},
                {"value": "Promoting your business","state": "idle"},
                {"value": "Selling to government","state": "idle"},
                {"value": "Training and learning new skills","state": "idle"}
            ],
            "freezeCurrentValues": True,
            "isFieldExpanded": False,
            "preventAutoSelect": False,
            "field": "cobj",
            "facetId": "cobj",
            "tabs": {},
            "activeTab": ""
        },
        {
            "filterFacetCount": True,
            "injectionDepth": 1000,
            "numberOfValues": 500,
            "sortCriteria": "automatic",
            "resultsMustMatch": "atLeastOneValue",
            "type": "specific",
            "currentValues": [
                {"value": "Less than 2 years","state": "idle"},
                {"value": "Between 2 and 5 years","state": "idle"},
                {"value": "More than 5 years","state": "idle"}
            ],
            "freezeCurrentValues": True,
            "isFieldExpanded": False,
            "preventAutoSelect": False,
            "field": "cbs",
            "facetId": "cbs",
            "tabs": {},
            "activeTab": ""
        },
        {
            "filterFacetCount": True,
            "injectionDepth": 1000,
            "numberOfValues": 500,
            "sortCriteria": "automatic",
            "resultsMustMatch": "atLeastOneValue",
            "type": "specific",
            "currentValues": [
                {"value": "Open","state": "selected"},
                {"value": "Coming soon","state": "selected"},
                {"value": "Closed","state": "idle"}
            ],
            "freezeCurrentValues": True,
            "isFieldExpanded": False,
            "preventAutoSelect": True,
            "field": "cgs",
            "facetId": "cgs",
            "tabs": {},
            "activeTab": ""
        },
        {
            "filterFacetCount": True,
            "injectionDepth": 1000,
            "numberOfValues": 500,
            "sortCriteria": "automatic",
            "resultsMustMatch": "atLeastOneValue",
            "type": "specific",
            "currentValues": [
                {"value": "Only show Indigenous business opportunities","state": "idle"},
                {"value": "Exclude Indigenous business opportunities","state": "idle"}
            ],
            "freezeCurrentValues": True,
            "isFieldExpanded": False,
            "preventAutoSelect": False,
            "field": "cib",
            "facetId": "cib",
            "tabs": {},
            "activeTab": ""
        }
    ],
    "numberOfResults": 10000,
    "firstResult": 0,
    "facetOptions": {"freezeFacetOrder": True},
    "maximumAge": 0
}

response = requests.post(url, headers=headers, json=payload)

content_str = response.content.decode('utf-8')
data = json.loads(content_str)

# Assuming your JSON is stored in a variable called `data`
results = data.get("results", [])

# Raise error and stop execution if no grants found
if not results:  # True if list is empty
    raise ValueError("No grants found on the webpage. The webpage structure may have changed.")

# Extract only the "raw" field
grantsListArr = [item["raw"] for item in results if "raw" in item]

for fields in grantsListArr:
    # Add timestamp for when entry is added
    fields['added_to_mongo_at'] = datetime.now(timezone.utc).isoformat()
    fields['title'] = fields['ctitle'] if 'ctitle' in fields else None
    fields['link'] = "https://business.gov.au" + fields['curl'] if 'curl' in fields else None

# Insert grant details into MongoDB
db = client["grants_db"]
collection = db["bga_grants"]

# Ensure unique index on 'title'
collection.create_index("title", unique=True)

if grantsListArr:
    updated_count = 0
    inserted_count = 0
    for grant in grantsListArr:
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