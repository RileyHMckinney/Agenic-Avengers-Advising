import json
import time
import random
from job_search_tool import search_jobs

# ---------------------------------------------------------
#  In-memory cache to suppress rapid duplicate invocations
# ---------------------------------------------------------
_last_invocations = {}
_THROTTLE_WINDOW = 3  # seconds


def recently_invoked(session_id: str, input_text: str) -> bool:
    key = f"{session_id}:{input_text}"
    now = time.time()
    if key in _last_invocations and now - _last_invocations[key] < _THROTTLE_WINDOW:
        return True
    _last_invocations[key] = now
    return False


def lambda_handler(event, context):
    print("Lambda invoked ✅")
    print(f"Incoming event: {json.dumps(event, indent=2)}")

    # Light random delay to prevent orchestration overlap
    time.sleep(random.uniform(0.1, 0.3))

    # Normalize body
    body = event.get("body", {})
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except Exception:
            body = {}

    # Extract query/location
    query = event.get("query") or body.get("query") or event.get("inputText")
    location = event.get("location") or body.get("location") or "Austin, Texas"

    if not query:
        print("❌ Missing query")
        return {
            "response": {
                "actionGroup": "JobSearchActionGroup",
                "apiPath": "/search",
                "httpMethod": "POST",
                "httpStatusCode": 400,
                "responseBody": {
                    "application/json": {
                        "body": json.dumps({"error": "Missing query parameter"})
                    }
                },
            }
        }

    # Prevent duplicate Bedrock retries within a few seconds
    if recently_invoked(event.get("sessionId", ""), query):
        print("🟡 Duplicate or rapid retry detected; skipping to avoid Bedrock loop.")
        return {
            "response": {
                "actionGroup": "JobSearchActionGroup",
                "apiPath": "/search",
                "httpMethod": "POST",
                "httpStatusCode": 429,
                "responseBody": {
                    "application/json": {
                        "body": json.dumps({"warning": "duplicate invocation ignored"})
                    }
                },
            }
        }

    print(f"Running search for: {query} in {location}")

    try:
        # Run job search with defensive timeout
        start = time.time()
        result = search_jobs(query=query, location=location, limit=10)
        elapsed = time.time() - start
        print(f"⏱️ SerpAPI search completed in {elapsed:.2f}s")

        jobs = result.get("jobs") or result.get("results") or []
        clean_jobs = [
            {
                "title": str(j.get("title", "")),
                "company": str(j.get("company", "")),
                "location": str(j.get("location", "")),
                "link": str(j.get("link", "")),
                "snippet": str(j.get("snippet", "")),
                "posted_at": str(j.get("posted_at", "")),
            }
            for j in jobs
        ][:5]  # ✅ Limit to 5 jobs for shorter Bedrock summarization

        count = len(clean_jobs)
        response_data = {
            "query": query,
            "location": location,
            "count": count,
            "jobs": clean_jobs,
            "next_page_token": result.get("next_page_token"),
        }

        print(f"✅ Returning {count} jobs to Bedrock Agent")
        body_json = json.dumps(response_data)

        # Optional diagnostic info
        print(f"Response size: {len(body_json)} bytes")

        return {
            "response": {
                "actionGroup": "JobSearchActionGroup",
                "apiPath": "/search",
                "httpMethod": "POST",
                "httpStatusCode": 200,
                "responseBody": {
                    "application/json": {"body": body_json}
                },
            }
        }

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {
            "response": {
                "actionGroup": "JobSearchActionGroup",
                "apiPath": "/search",
                "httpMethod": "POST",
                "httpStatusCode": 500,
                "responseBody": {
                    "application/json": {
                        "body": json.dumps({"error": str(e)})
                    }
                },
            }
        }
