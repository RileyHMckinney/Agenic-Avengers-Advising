# agent_bedrock.py
import os, json, boto3
from tools.tool_wrappers.job_search_tool import JobSearchTool

MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
REGION = os.getenv("AWS_REGION", "us-east-1")

bedrock = boto3.client("bedrock-runtime", region_name=REGION)
tool = JobSearchTool(mode=os.getenv("JOB_TOOL_MODE", "local"))

def agent_handle(user_message: str):
    prompt = f"""
You are an API function caller. Output *only* valid JSON — nothing else.
If the user asks for jobs, extract the job title/role and location.

Rules:
- Return ONLY valid JSON, no prose or explanations.
- The JSON must contain exactly these keys: "query" and "location".
- If no job intent is detected, return: {{"query": null, "location": null}}.

User message:
{user_message}
    """.strip()

    body = json.dumps({
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
        "anthropic_version": "bedrock-2023-05-31"
    })

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=body,
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())

    # Claude 3 responses put text in result["content"][0]["text"]
    text = ""
    if "content" in result and isinstance(result["content"], list):
        for item in result["content"]:
            if item.get("type") == "text":
                text += item.get("text", "")
    text = text.strip()

    print("DEBUG: Raw model output >>>", repr(text))

    try:
        args = json.loads(text)
    except json.JSONDecodeError:
        return {"error": f"Model returned non-JSON output: {text}"}

    if not args.get("query"):
        return {"message": "I'm here to help with job searches. Try asking for a role or city."}

    query = args["query"]
    location = args.get("location")
    results = tool.run(query=query, location=location, limit=3)
    return results
