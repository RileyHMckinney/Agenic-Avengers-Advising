# lambda_handler.py
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
    # ensure we will encode as UTF-8 safely
    return s

def lambda_handler(event: Dict[str, Any], context):
    # log input for debugging in CloudWatch
    try:
        logger.debug("EVENT (raw): %s", json.dumps(event, ensure_ascii=False))
    except Exception:
        logger.debug("EVENT (raw, repr): %r", event)

    try:
        # Example parameter extraction (adapt to your real schema)
        params = event.get("parameters") or event.get("functionParameters") or {}
        if isinstance(params, list):
            # optional: your earlier helper to normalize
            pmap = {}
            for itm in params:
                if isinstance(itm, dict) and "name" in itm:
                    pmap[itm["name"]] = itm.get("value")
            params = pmap

        goal = params.get("goal") or params.get("Goal") or event.get("query") or "unknown goal"
        gap_skills = params.get("gap_skills") or params.get("gaps") or []
        if isinstance(gap_skills, str) and "," in gap_skills:
            gap_skills = [x.strip() for x in gap_skills.split(",") if x.strip()]

        # Build a concise response text
        text = f"Goal: {_safe_text(goal)}\nMissing skills: {_safe_text(gap_skills)}\nSuggested: Example Project A, Project B"

        # Ensure UTF-8 compatibility
        text = _safe_text(text)

        response_payload = {
            "response": {
                "actionGroup": event.get("actionGroup", "ProjectAdvisorGroup"),
                "function": event.get("function", "advise_projects"),
                "functionResponse": {
                    "responseBody": {
                        # IMPORTANT: Bedrock agent tooling often expects uppercase TEXT key
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
        logger.exception("Unhandled exception in lambda")
        fallback = {"response": {"actionGroup": "ProjectAdvisorGroup", "function": "advise_projects",
                                 "functionResponse": {"responseBody": {"TEXT": {"body": f"Error: {str(e)}"}}}}}
        return fallback
