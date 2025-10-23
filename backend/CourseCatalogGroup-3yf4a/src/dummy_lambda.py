import json
import logging
from typing import Any, Dict

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def _safe_text(s: Any) -> str:
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)
    return s

def lambda_handler(event: Dict[str, Any], context):
    try:
        logger.debug("EVENT: %s", json.dumps(event, ensure_ascii=False))
        params = event.get("parameters") or event.get("functionParameters") or {}
        topic = params.get("topic") or params.get("skill") or "unspecified"

        # Simulated response (later, you can connect this to the UTD course KB)
        course_matches = [
            {"course": "CS 4375 - Machine Learning", "skills": ["ML algorithms", "Python", "data processing"]},
            {"course": "CS 4391 - Introduction to AI", "skills": ["neural networks", "probability", "search algorithms"]},
            {"course": "STAT 4355 - Data Analysis for Machine Learning", "skills": ["statistics", "pandas", "model evaluation"]}
        ]

        text = f"Courses at UTD related to '{topic}':\n"
        for c in course_matches:
            text += f"- {c['course']} (skills: {', '.join(c['skills'])})\n"

        response_payload = {
            "response": {
                "actionGroup": event.get("actionGroup", "CourseCatalogGroup"),
                "function": event.get("function", "find_courses"),
                "functionResponse": {
                    "responseBody": {
                        "TEXT": {
                            "body": text
                        }
                    }
                }
            }
        }

        logger.debug("Returning payload: %s", json.dumps(response_payload, ensure_ascii=False)[:2000])
        return response_payload

    except Exception as e:
        logger.exception("Error in Lambda")
        return {
            "response": {
                "actionGroup": "CourseCatalogGroup",
                "function": "find_courses",
                "functionResponse": {
                    "responseBody": {
                        "TEXT": {
                            "body": f"Error: {str(e)}"
                        }
                    }
                }
            }
        }