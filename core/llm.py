# import openai
from transformers import pipeline
import re
from openai import OpenAI, OpenAIError
import os
from dotenv import load_dotenv

load_dotenv()


def get_inclusion_criteria_from_data(data):

    inclusion_match = re.search(
        r"Inclusion Criteria:(.*?)(Exclusion Criteria:|$)", data, re.S)

    inclusion_criteria = inclusion_match.group(
        1).strip() if inclusion_match else ""

    return inclusion_criteria


def extract_diseases_from_inclusion_criteria(data):
    try:
        # Extract only inclusion criteria from raw text
        inclusion_criteria = get_inclusion_criteria_from_data(data)

        # Load open-ai api key
        key = os.getenv('OPENAI_API_KEY')

        client = OpenAI(api_key=key)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                    "content": "You are an assistant extracting health-related terms."},
                {"role": "user", "content": "Extract any diseases or conditions mentioned in the text give onlt extracted text without any text if no text is found then return none:"},
                {"role": "user", "content": f"{inclusion_criteria}"}

            ]
        )

        extracted_text = completion.choices[0].message.content.strip()

        # Get list of diseases/conditions
        conditions = [condition.strip()
                      for condition in extracted_text.split("\n") if condition.strip()]

        return conditions
    except OpenAIError as api_err:
        print(f"OpenAI API error occurred: {api_err}")
        return []

    except (KeyError, IndexError) as parse_err:
        print(f"Parsing error occurred in the response: {parse_err}")
        return []

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
