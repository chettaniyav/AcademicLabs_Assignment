from api import fetch_studies
from mapper import map_study_to_schema
from db import get_database, insert_studies


studies = fetch_studies()
mapped_studies = [map_study_to_schema(study) for study in studies if study]
db = get_database()
insert_studies(db, mapped_studies)
print(f"Inserted {len(mapped_studies)} studies into monogodb")
