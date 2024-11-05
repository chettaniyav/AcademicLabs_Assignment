import requests
from datetime import datetime
import urllib.parse

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"


def fetch_studies(start_date="2024-10-20", end_date="2024-10-21", page_size=1000):
    studies = []
    headers = {}
    params = {

        "format": "json",
        "query.term": f"AREA[StartDate]RANGE[{start_date},{end_date}]",
        "countTotal": 'true',
        "pageSize": page_size
    }
    params = urllib.parse.urlencode(params, safe="[],:")
    response = requests.get(url=BASE_URL, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    studies.extend(data.get("studies", []))

    return studies
