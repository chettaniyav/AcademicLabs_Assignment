from api import fetch_studies
from mapper import map_study_to_schema
from db import get_database, insert_studies
from llm import process_studies

# Call clinicaltrials.gov for data
studies = fetch_studies()
# Process data in mini-batches
all_mapped_studies = process_studies(studies)
db = get_database()
# Add data to DB
insert_studies(db, all_mapped_studies)
print(f"Inserted {len(all_mapped_studies)} studies into monogodb")
