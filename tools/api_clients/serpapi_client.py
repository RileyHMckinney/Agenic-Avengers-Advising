# tools/api_clients/serpapi_client.py
import os
import time
import json
import requests
from typing import Dict, Any, Optional

# boto3 import is lazy (only used when we need to read secrets)
try:
    import boto3
    from botocore.exceptions import ClientError
except Exception:
    boto3 = None
    ClientError = Exception

class SerpApiClient:
    # simple in-process cache so we don't hit Secrets Manager on every request
    _cached_key: Optional[str] = None
    _cached_at: float = 0.0
    _cache_ttl: int = 300  # seconds

    def __init__(self, api_key: Optional[str] = None, secret_name_env: str = "SERPAPI_SECRET_NAME", region_name: Optional[str] = None):
        """
        If api_key is provided it's used directly.
        Otherwise we try (in order):
         1) os.environ['SERPAPI_KEY']
         2) read secret from Secrets Manager using the secret name in env var `SERPAPI_SECRET_NAME`
        region_name: optional boto3 region (defaults to AWS_REGION env var or us-east-1)
        """
        self.region_name = region_name or os.getenv("AWS_REGION") or "us-east-1"
        self.base = "https://serpapi.com/search.json"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "AgenicAvengersBot/1.0"})

        # Determine API key
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        if not self.api_key:
            secret_name = os.getenv(secret_name_env)
            if secret_name:
                self.api_key = self._get_key_from_secrets(secret_name, region_name=self.region_name)
        if not self.api_key:
            raise ValueError(
                "SerpApi key not provided. Set SERPAPI_KEY env var, pass api_key to SerpApiClient(), "
                "or set SERPAPI_SECRET_NAME to a Secrets Manager secret."
            )

    @classmethod
    def _is_cache_valid(cls) -> bool:
        return cls._cached_key is not None and (time.time() - cls._cached_at) < cls._cache_ttl

    @classmethod
    def _update_cache(cls, key: str):
        cls._cached_key = key
        cls._cached_at = time.time()

    def _get_key_from_secrets(self, secret_name: str, region_name: Optional[str] = None) -> str:
        """
        Fetch secret value from AWS Secrets Manager. Expects the secret to be JSON:
          {"SERPAPI_KEY": "your_key_here"}
        or a plain string containing the key.
        Caches the key in memory for _cache_ttl seconds.
        """
        # return cached if still valid
        if SerpApiClient._is_cache_valid():
            return SerpApiClient._cached_key  # type: ignore

        if boto3 is None:
            raise RuntimeError("boto3 is required to read secrets from AWS Secrets Manager but it is not available.")

        client = boto3.client("secretsmanager", region_name=region_name or self.region_name)
        try:
            resp = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            # bubble up with a helpful message
            raise RuntimeError(f"Unable to read secret '{secret_name}' from Secrets Manager: {e}") from e

        secret_string = resp.get("SecretString")
        if secret_string is None:
            raise RuntimeError(f"Secret '{secret_name}' had no SecretString")

        # Try JSON first, fallback to raw string
        try:
            parsed = json.loads(secret_string)
            # try common keys
            key = parsed.get("SERPAPI_KEY") or parsed.get("serpapi_key") or parsed.get("key") or parsed.get("api_key")
            if not key:
                # if JSON but doesn't include our key, raise useful error
                raise RuntimeError(f"Secret '{secret_name}' JSON found but did not contain a 'SERPAPI_KEY' field.")
        except json.JSONDecodeError:
            # plain-text secret: assume it is the key itself
            key = secret_string

        # cache and return
        SerpApiClient._update_cache(key)
        return key

    def search_google_jobs(self, query: str, location: Optional[str] = None, limit: int = 10, next_page_token: Optional[str] = None) -> Dict[str, Any]:
        import re, json
        # normalize inputs
        q = (query or "").strip()
        loc = (location or "").strip() if location is not None else None

        omit_location = False
        if not loc or (isinstance(loc, str) and loc.lower() == "remote"):
            omit_location = True
            if "remote" not in q.lower():
                q = f"{q} remote"

        num = min(int(limit), 10)
        params = {
            "engine": "google_jobs",
            "q": q,
            "api_key": self.api_key,
            "num": num
        }
        if not omit_location:
            params["location"] = loc
        if next_page_token:
            params["next_page_token"] = next_page_token

        resp = self.session.get(self.base, params=params, timeout=20)
        try:
            data = resp.json()
        except ValueError:
            resp.raise_for_status()

        serpapi_error = data.get("error")
        status = (data.get("search_metadata") or {}).get("status")
        if serpapi_error or (status and str(status).lower() != "success"):
            detail = serpapi_error or data.get("search_metadata") or data
            raise RuntimeError(f"SerpApi returned an error: {detail}")

        # url regex + recursive finder
        url_re = re.compile(r"https?://[^\s'\"<>]+")
        def find_first_url_in_obj(obj):
            if obj is None: return None
            if isinstance(obj, str):
                m = url_re.search(obj); return m.group(0) if m else None
            if isinstance(obj, dict):
                # prefer known link keys (explicit)
                for prefer in ("share_link","link", "serpapi_job_link", "serpapi_link", "apply_link", "job_link", "url", "apply_url"):
                    v = obj.get(prefer)
                    if isinstance(v, str) and url_re.search(v):
                        return url_re.search(v).group(0)
                for v in obj.values():
                    found = find_first_url_in_obj(v)
                    if found: return found
            if isinstance(obj, (list, tuple)):
                for v in obj:
                    found = find_first_url_in_obj(v)
                    if found: return found
            return None

        def raw_preview_of_item(item, max_chars=600):
            s = json.dumps(item, ensure_ascii=False) if not isinstance(item, str) else item
            return (s if len(s) <= max_chars else s[:max_chars].rsplit(" ",1)[0] + "…")

        # safe extractor for posted_at inside extensions (handles dict or list)
        def extract_posted_at_from_extensions(item):
            ext = item.get("extensions")
            if not ext:
                return None
            # if extensions is a dict
            if isinstance(ext, dict):
                return ext.get("posted_at") or ext.get("posted")
            # if extensions is a list, search for a dict that has posted_at
            if isinstance(ext, (list, tuple)):
                for e in ext:
                    if isinstance(e, dict):
                        # common keys
                        if "posted_at" in e:
                            return e.get("posted_at")
                        if "posted" in e:
                            return e.get("posted")
                        # sometimes nested in detected_extensions
                        de = e.get("detected_extensions") if isinstance(e.get("detected_extensions"), dict) else None
                        if de and "posted_at" in de:
                            return de.get("posted_at")
            return None

        def _extract_job_fields(item: dict) -> dict:
            # explicit preferred keys (including share_link)
            link = None
            for k in ("share_link","link","serpapi_job_link","serpapi_link","apply_link","job_link","url","apply_url"):
                v = item.get(k)
                if isinstance(v, str) and url_re.search(v):
                    link = url_re.search(v).group(0)
                    break
            if not link:
                nested = item.get("serpapi_result") or item.get("result") or item.get("raw")
                if isinstance(nested, dict):
                    for k in ("share_link","link","serpapi_job_link","serpapi_link","apply_link","job_link","url","apply_url"):
                        v = nested.get(k)
                        if isinstance(v, str) and url_re.search(v):
                            link = url_re.search(v).group(0)
                            break
            if not link:
                link = find_first_url_in_obj(item)

            # prefer 'description' then 'snippet'
            raw_snippet = item.get("description") or item.get("snippet") or item.get("raw_description") or ""
            snippet = (raw_snippet or "").strip()
            if len(snippet) > 800:
                snippet = snippet[:800].rsplit(" ", 1)[0] + "…"

            posted_at = item.get("posted_at") or extract_posted_at_from_extensions(item) or (item.get("extensions") if isinstance(item.get("extensions"), str) else None)

            return {
                "title": item.get("title") or item.get("job_title"),
                "company": item.get("company_name") or item.get("company") or item.get("via") or item.get("hiring_organization"),
                "link": link,
                "snippet": snippet,
                "location": item.get("location"),
                "posted_at": posted_at,
                "job_id": item.get("job_id"),
                "source": item.get("via") or item.get("source") or item.get("site") or item.get("provider"),
                "raw_preview": None if link else raw_preview_of_item(item, max_chars=500)
            }

        jobs = []
        primary_list = data.get("jobs_results") or data.get("jobs") or data.get("organic_results") or []
        for item in primary_list[:num]:
            jobs.append(_extract_job_fields(item))

        if not jobs:
            for alt_key in ("jobs_results","jobs","organic_results","results"):
                for item in data.get(alt_key, [])[:num]:
                    jobs.append(_extract_job_fields(item))
                if jobs: break

        # get next_page_token
        next_token = None
        serpapi_pagination = data.get("serpapi_pagination") or {}
        if isinstance(serpapi_pagination, dict):
            next_token = serpapi_pagination.get("next_page_token")
        if not next_token:
            nested_pag = (data.get("search_metadata") or {}).get("serpapi_pagination") or {}
            if isinstance(nested_pag, dict):
                next_token = nested_pag.get("next_page_token")

        return {
            "query": q,
            "location": None if omit_location else loc,
            "results": jobs,
            "next_page_token": next_token,
            "raw": data
        }

