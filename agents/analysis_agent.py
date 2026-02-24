from ollama import Client
import json
import logging
from schemas import CompanyAnalysis
from pydantic import ValidationError

client = Client(host="http://host.docker.internal:11434")
logger = logging.getLogger(__name__)


import re

def extract_json(text: str) -> str:
    """
    Extract JSON from markdown code blocks or raw text
    """

    # remove ```json and ```
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)

    # find first { and last }
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        return text[start:end+1]

    return text

def analyze_company(company, data):

    prompt = f"""
        You are a senior business analyst.

        Analyze the company using the provided data.

        Return ONLY valid JSON.

        Rules:
        - Do NOT explain instructions
        - Do NOT explain JSON structure
        - Do NOT explain variables
        - ONLY analyze the company
        - Be specific and factual

        Company: {company}

        Data:
        {data}

        Return JSON in this format:

        {{
        "company": "{company}",
        "summary": "clear business summary",
        "strengths": ["strength1", "strength2"],
        "weaknesses": ["weakness1", "weakness2"],
        "competitors": ["competitor1", "competitor2"]
        }}
    """

    try:
        response = client.chat(
            model="gemma:2b",
            messages=[{"role": "user", "content": prompt}]
        )

        result_text = response["message"]["content"]

        try:
            clean_text = extract_json(result_text)

            raw_json = json.loads(clean_text)

            validated = CompanyAnalysis(**raw_json)

            return validated.dict()

        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning("Invalid structured output for %s: %s", company, str(e))

            fallback = CompanyAnalysis(
                company=company,
                summary=result_text,
                strengths=[],
                weaknesses=[],
                competitors=[]
            )

            return fallback.dict()

    except Exception as e:
        logger.exception("Failed to analyze company %s", company)

        fallback = CompanyAnalysis(
            company=company,
            summary=f"Error during analysis: {str(e)}",
            strengths=[],
            weaknesses=[],
            competitors=[]
        )

        return fallback.dict()
    