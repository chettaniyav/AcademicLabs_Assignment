# import openai
import logging
import re
from openai import OpenAI, OpenAIError
import os
from dotenv import load_dotenv
from tqdm import tqdm
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from logger_config import get_logger

from mapper import map_study_to_schema
# Load OpenAI Keys
load_dotenv()

logger = get_logger("_llm_")

# Change the number mini-batches here for openai processing
BATCH_SIZE = 20


def get_inclusion_criteria_from_data(data):

    inclusion_match = re.search(
        r"Inclusion Criteria:(.*?)(Exclusion Criteria:|$)", data, re.S)

    inclusion_criteria = inclusion_match.group(
        1).strip() if inclusion_match else ""

    return inclusion_criteria


def get_inclusion_criteria_from_batch(studies):
    """Extract inclusion criteria from a batch of studies."""
    inclusion_criteria_batch = []
    study_ids = []

    for study in studies:
        protocol = study.get("protocolSection", {})
        identification = protocol.get("identificationModule", {})
        study_id = identification.get("nctId", "unknown")

        eligibility = protocol.get("eligibilityModule", {})
        text = eligibility.get("eligibilityCriteria", "").strip()
        text = get_inclusion_criteria_from_data(text)
        inclusion_criteria_batch.append(text)
        study_ids.append(study_id)

    return inclusion_criteria_batch, study_ids


def batch_extract_diseases_from_criteria(criteria_batch, study_ids):
    """Extract diseases from a batch of criteria """
    try:
        # Add study ID as a prefix to each criteria
        marked_criteria = [f"Study {sid}:\n{
            text}" for sid, text in zip(study_ids, criteria_batch)]
        combined_text = "\n===STUDY_SEPARATOR===\n".join(marked_criteria)

        key = os.getenv('OPENAI_API_KEY')
        client = OpenAI(api_key=key)

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                    "content": "You are an assistant extracting health condtions from text."},
                {"role": "user", "content": """
                    For each study separated by ===STUDY_SEPARATOR===, extract diseases or conditions.
                    Format your response as:
                    Study <ID>:
                    - condition1
                    - condition2
                    
                    If no conditions found, respond with:
                    Study <ID>:
                    - None
                    
                    Maintain this exact format for each study.
                """},
                {"role": "user", "content": combined_text}
            ]
        )

        extracted_text = completion.choices[0].message.content.strip()

        # Split response by study and parse conditions
        study_responses = extracted_text.split("Study")
        study_responses = [resp for resp in study_responses if resp.strip()]

        # Initialize results with "None" for each study
        results = [["None"] for _ in range(len(criteria_batch))]

        # Parse each study's response
        for response in study_responses:
            try:
                # Extract study ID and conditions
                study_id_text, conditions_text = response.split(":", 1)
                study_id = study_id_text.strip()

                # Find the index of this study in our original batch
                if study_id in study_ids:
                    idx = study_ids.index(study_id)

                    # Extract conditions
                    conditions = [
                        cond.strip("- ").strip()
                        for cond in conditions_text.strip().split("\n")
                        if cond.strip("- ").strip()
                    ]

                    results[idx] = conditions if conditions else ["None"]
            except Exception as e:
                logger.error(f"Error parsing response for study: {study_id}")
                continue

        # Verify we have the correct number of results
        if len(results) != len(criteria_batch):
            logger.warning(f"Size mismatch: got {len(results)} results for {
                           len(criteria_batch)} studies")

        return results

    except OpenAIError as api_err:
        logger.error(f"OpenAI API error occurred: {api_err}")
        return [["None"] for _ in criteria_batch]

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return [["None"] for _ in criteria_batch]


def batch_process_studies(studies, batch_size=BATCH_SIZE):
    """Process studies in batches with progress tracking and error handling."""
    all_results = []

    try:
        for i in tqdm(range(0, len(studies), batch_size), desc="Processing studies"):
            batch = studies[i:i + batch_size]

            # Get eligibility criteria and study IDs
            eligibility_batch, study_ids = get_inclusion_criteria_from_batch(
                batch)

            # Extract conditions with study ID tracking
            batch_conditions = batch_extract_diseases_from_criteria(
                eligibility_batch, study_ids)

            # Map studies to schema
            batch_results = []
            for study, conditions in zip(batch, batch_conditions):
                mapped_study = map_study_to_schema(study, conditions)
                # Only add successfully mapped studies
                if mapped_study:
                    batch_results.append(mapped_study)

            all_results.extend(batch_results)

            # Logging progress
            logger.info(f"Processed batch {
                        i//batch_size + 1}: {len(batch_results)} studies")

    except Exception as e:
        logger.error(f"Error in batch processing: {e}")

    return all_results


def process_studies(studies_data, batch_size=BATCH_SIZE):
    """Main function to process studies and logging """
    try:
        logger.info(f"Starting to process {len(studies_data)} studies")
        results = batch_process_studies(studies_data, batch_size)
        logger.info(f"Successfully processed {len(results)} studies")
        return results
    except Exception as e:
        logger.error(f"Failed to process studies: {e}")
        return []
