# tools/tool_wrappers/job_search_tool.py
import os
import json
import time
from typing import Optional, Dict, Any

# Lazy imports: boto3 only if needed
try:
    import boto3
except Exception:
    boto3 = None

# If local mode: import your client
try:
    from tools.api_clients.serpapi_client import SerpApiClient
except Exception:
    # helpful message if running from different cwd
    SerpApiClient = None

class JobSearchTool:
    def __init__(self, mode: str = "local", lambda_name: Optional[str] = None, region_name: Optional[str] = None):
        """
        mode: "local" or "lambda"
        lambda_name: name/ARN of the deployed lambda to invoke when mode='lambda'
        region_name: AWS region
        """
        self.mode = mode
        self.region_name = region_name or os.getenv("AWS_REGION") or "us-east-1"
        self.lambda_name = lambda_name or os.getenv("SERPAPI_LAMBDA_NAME") or "serpapi-google-jobs"

        if self.mode == "local" and SerpApiClient is None:
            raise RuntimeError("SerpApiClient not importable. Check PYTHONPATH and project layout.")

        if self.mode == "lambda" and boto3 is None:
            raise RuntimeError("boto3 required for lambda mode but not installed.")

        if self.mode == "local":
            # pass None to SarpApiClient so it uses env or secrets manager
            self.client = SerpApiClient()
        else:
            self.lambda_client = boto3.client("lambda", region_name=self.region_name)

    def run(self, query: str, location: Optional[str] = None, limit: int = 10, next_page_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a job search. Returns a dict with keys:
          - query, location, results (list), next_page_token, raw (optional)
        """
        if self.mode == "local":
            return self._run_local(query, location, limit, next_page_token)
        else:
            return self._run_lambda(query, location, limit, next_page_token)

    def _run_local(self, query: str, location: Optional[str], limit: int, next_page_token: Optional[str]) -> Dict[str, Any]:
        # Local call to SerpApiClient
        # Keep returned format consistent with lambda output
        resp = self.client.search_google_jobs(query=query, location=location, limit=limit, next_page_token=next_page_token)
        return resp

    def _run_lambda(self, query: str, location: Optional[str], limit: int, next_page_token: Optional[str]) -> Dict[str, Any]:
        # Invoke lambda synchronously (RequestResponse)
        payload = {
            "query": query,
            "location": location,
            "limit": int(limit),
        }
        if next_page_token:
            payload["next_page_token"] = next_page_token

        resp = self.lambda_client.invoke(
            FunctionName=self.lambda_name,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload).encode("utf-8")
        )

        # Lambda returns something like {"statusCode":200,"body":"<json string>"}
        # read and decode
        raw_stream = resp.get("Payload")
        if raw_stream is None:
            raise RuntimeError("No payload returned from lambda invoke")

        body_bytes = raw_stream.read()
        try:
            lambda_response = json.loads(body_bytes.decode("utf-8"))
        except Exception as e:
            raise RuntimeError(f"Could not decode lambda payload: {e}\nraw: {body_bytes[:400]!r}")

        # if lambda_response wraps in HTTP-like statusCode/body, unwind
        if isinstance(lambda_response, dict) and "statusCode" in lambda_response and "body" in lambda_response:
            try:
                body = json.loads(lambda_response["body"])
            except Exception:
                # maybe it's already a dict
                body = lambda_response["body"]
        else:
            body = lambda_response

        return body
