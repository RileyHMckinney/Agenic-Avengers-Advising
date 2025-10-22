# agent_bedrock.py
import os, json, boto3
from tools.tool_wrappers.job_search_tool import JobSearchTool
from tools.tool_wrappers.memory_tool import MemoryTool

MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
REGION = os.getenv("AWS_REGION", "us-east-1")

# Initialize core tools
memory_tool = MemoryTool(region=REGION)
bedrock = boto3.client("bedrock-runtime", region_name=REGION)
tool = JobSearchTool(mode=os.getenv("JOB_TOOL_MODE", "local"))

def agent_handle(user_message: str, user_id: str):
    """
    Main agent handler. Keeps separate memory for each user.
    user_id should be a unique ID string per user (email, UUID, session ID, etc.)
    """

    # Step 1: Load prior memory (if any)
    memory = memory_tool.load_memory(user_id) or {}
    memory_context = json.dumps(memory, indent=2) if memory else "No previous data."

    # Step 2: Build a context-aware prompt
    prompt = f"""
    You are an intelligent API function caller and personal job assistant.

    User memory:
    {memory_context}

    The user said:
    "{user_message}"

    Task:
    - If the user is asking for jobs, extract job "query" (role/title) and "location".
    - If they mention new skills or resume info, include that under a "resume" field.
    - If no job-related intent exists, return:
        {{ "query": null, "location": null, "resume": null }}

    Return ONLY valid JSON, no explanations.
    """

    # Step 3: Call Bedrock (Claude model)
    body = json.dumps({
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "anthropic_version": "bedrock-2023-05-31"
    })

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=body,
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())

    # Extract model output text
    text = ""
    for item in result.get("content", []):
        if item.get("type") == "text":
            text += item.get("text", "")
    text = text.strip()

    print("DEBUG: Raw model output >>>", repr(text))

    # Step 4: Parse the JSON from Claude
    try:
        args = json.loads(text)
    except json.JSONDecodeError:
        return {"error": f"Model returned invalid JSON: {text}"}

    # Step 5: Update memory if resume or skills mentioned
    if args.get("resume"):
        memory["resume_text"] = args["resume"]

    # Step 6: If job query detected, perform search
    if args.get("query"):
        query = args["query"]
        location = args.get("location")
        memory["last_query"] = query
        memory["last_location"] = location
        memory_tool.save_memory(user_id, memory)
        results = tool.run(query=query, location=location, limit=3)
        return {"user_id": user_id, "results": results, "memory": memory}

    # Step 7: If no job query, still update memory (if changed)
    if memory:
        memory_tool.save_memory(user_id, memory)

    return {"message": "I'm ready to help find jobs or store resume details!", "memory": memory}
