from ollama import Client
import json
import logging
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)
client = Client(host="http://host.docker.internal:11434")

class DecisionOutput(BaseModel):

    company: str
    investment_recommendation: str
    risk_level: str
    market_position: str
    reasoning: str


def make_decision(company, analysis):

    prompt = f"""
        You are a senior investment strategist.

        Your task is to analyze the company and return ONLY a valid JSON object.

        IMPORTANT RULES:
        - Select EXACTLY ONE value for each field.
        - DO NOT list multiple options.
        - DO NOT repeat the allowed options.
        - DO NOT explain outside JSON.
        - DO NOT include markdown.
        - DO NOT include headings.
        - DO NOT include extra text.
        - Output ONLY the JSON object.

        Company:
        {company}

        Analysis:
        {analysis}

        Allowed values:

        investment_recommendation: Strong Buy, Buy, Hold, Avoid
        risk_level: Low, Medium, High
        market_position: Leader, Strong Competitor, Emerging, Weak

        Return EXACTLY this JSON structure:

        {{
        "company": "{company}",
        "investment_recommendation": "<ONE selected value>",
        "risk_level": "<ONE selected value>",
        "market_position": "<ONE selected value>",
        "reasoning": "<clear concise reasoning based on analysis>"
        }}

        Correct example format (example only):

        {{
        "company": "Tesla",
        "investment_recommendation": "Buy",
        "risk_level": "Medium",
        "market_position": "Leader",
        "reasoning": "Strong growth, dominant EV position, but valuation risk exists."
        }}

        Now return the JSON:
        """

    try:

        response = client.chat(
            model="gemma:2b",
            messages=[{"role": "user", "content": prompt}]
        )

        text = response["message"]["content"].strip()

        if not text:
            raise ValueError("Empty response from LLM")

        # remove markdown if present
        text = text.replace("```json", "").replace("```", "").strip()

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON found in LLM response")

        json_text = text[start:end+1]

        decision_dict = json.loads(json_text)

        validated = DecisionOutput(**decision_dict)

        return validated.dict()

    except ValidationError as e:

        logger.warning("Decision validation failed: %s", e)

        return {
            "company": company,
            "investment_recommendation": "Unknown",
            "risk_level": "Unknown",
            "market_position": "Unknown",
            "reasoning": "Validation failed"
        }

    except Exception as e:

        logger.exception("Decision agent failed")

        return {
            "company": company,
            "investment_recommendation": "Unavailable",
            "risk_level": "Unavailable",
            "market_position": "Unavailable",
            "reasoning": f"Decision agent error: {str(e)}"
        }