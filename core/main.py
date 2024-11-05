from api import fetch_studies
from mapper import map_study_to_schema
from db import get_database, insert_studies

# Call clinicaltrials.gov for data
studies = fetch_studies()

# Map data according to example json in assignment
mapped_studies = [map_study_to_schema(study) for study in studies if study]
# Init DB conn
db = get_database()
# Add data to DB
insert_studies(db, mapped_studies)
print(f"Inserted {len(mapped_studies)} studies into monogodb")
