import os
import json
from typing import Optional, Dict, Any, List
from serpapi_client import SerpApiClient

# ---------------------------------------------------------
# 🔁 Persistent SerpApiClient cache (survives warm invocations)
# ---------------------------------------------------------
_cached_client: Optional[SerpApiClient] = None


def _get_client(region: Optional[str] = None) -> SerpApiClient:
    """
    Returns a cached SerpApiClient instance to avoid re-initialization on every Lambda invoke.
    """
    global _cached_client
    if _cached_client is None:
        region_to_use = region or os.getenv("AWS_REGION") or "us-east-1"
        print(f"🔧 Initializing new SerpApiClient for region={region_to_use}")
        _cached_client = SerpApiClient(region_name=region_to_use)
    return _cached_client


def search_jobs(
    query: str,
    location: Optional[str] = None,
    limit: int = 10,
    pages: int = 1,
    region: Optional[str] = None
) -> Dict[str, Any]:
    """
    Queries SerpAPI for job listings and returns a clean, summarized structure.
    Uses a cached SerpApiClient for performance across warm invocations.
    """
    client = _get_client(region)

    # Fetch results
    data = client.search_google_jobs(query=query, location=location, limit=limit)
    jobs = data.get("results", [])
    next_token = data.get("next_page_token")

    # Format the jobs for readability
    formatted_jobs: List[Dict[str, Any]] = []
    for job in jobs:
        formatted_jobs.append({
            "title": job.get("title"),
            "company": job.get("company"),
            "location": job.get("location"),
            "posted_at": job.get("posted_at"),
            "snippet": (job.get("snippet") or "")[:180] + "…" if job.get("snippet") else None,
            "link": job.get("link"),
        })

    # Build clean response
    summary = {
        "query": data.get("query"),
        "location": data.get("location"),
        "count": len(formatted_jobs),
        "next_page_token": next_token,
        "jobs": formatted_jobs,
    }

    # Optional: short console summary
    print(f"\n✅ Found {len(formatted_jobs)} job(s) for '{query}'" +
          (f" in {location}" if location else "") + ":")

    for j in formatted_jobs[:5]:
        print(f" - {j['title']} at {j['company']} ({j['location']})")

    return summary
