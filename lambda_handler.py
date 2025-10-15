# lambda_handler.py
import os
import json
from typing import Any, Dict

from tools.tool_wrappers.job_search_tool import search_jobs

def _response(status: int, body: Any) -> Dict[str, Any]:
    return {"statusCode": status, "headers": {"Content-Type": "application/json"}, "body": json.dumps(body, ensure_ascii=False)}

def lambda_handler(event, context):
    """
    Expected event (API GW or direct invoke):
    {
      "query": "software engineer intern",
      "location": "Austin, TX" | null,
      "limit": 10,
      "pages": 2
    }
    """
    try:
        body = event.get("body") if isinstance(event, dict) else None
        if isinstance(body, str):
            body = json.loads(body)
        payload = body or event or {}
        query = payload.get("query") or payload.get("q")
        if not query:
            return _response(400, {"error": "missing 'query' parameter"})
        location = payload.get("location")
        limit = int(payload.get("limit", 10))
        pages = int(payload.get("pages", 1))
        region = os.environ.get("AWS_REGION", None)
        res = search_jobs(query=query, location=location, limit=limit, pages=pages, region=region)
        return _response(200, res)
    except Exception as e:
        # never return secrets or raw exceptions in production; for dev we show message
        return _response(500, {"error": str(e)})
