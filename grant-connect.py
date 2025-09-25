import requests
from bs4 import BeautifulSoup
import csv

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
                detailDivArr = grantSoup.find_all("div", class_="list-desc")
                for detailDiv in detailDivArr:
                    grantDetailTitle = detailDiv.find("span").get_text()
                    grantDetailDescription = detailDiv.find("div", class_="list-desc-inner").get_text(strip=True, separator=" ")
                    grantDetailsObj[grantDetailTitle] = grantDetailDescription
                
                grantListArr.append(grantDetailsObj)

# Get a list of all property names in grantListArr objects
property_names = set()
for grant in grantListArr:
    property_names.update(grant.keys())
property_names = list(property_names)

# Move 'GO ID:' to the front if it exists
if 'GO ID:' in property_names:
    property_names.remove('GO ID:')
    property_names.insert(0, 'GO ID:')

# Write the grant details to a CSV file
with open("grant-connect.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=property_names)
    writer.writeheader()
    for grant in grantListArr:
        writer.writerow(grant)
