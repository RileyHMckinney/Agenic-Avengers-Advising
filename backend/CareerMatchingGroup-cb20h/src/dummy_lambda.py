import json
import boto3
from botocore.config import Config

# ===============================================================
# ⚙️ Global client + configuration
# ===============================================================
bedrock = boto3.client(
    "bedrock-agent-runtime",
    config=Config(read_timeout=60, connect_timeout=10, retries={"max_attempts": 2}),
)

AGENTS = {
    "job":     ("NZI8TPUR3R", "GEXWIDRZ1M"),
    "course":  ("OEH7N71AUQ", "GG3PK36DC4"),
    "project": ("H4HK5PVH9W", "BNOQXCGRDA"),
    "resume":  ("LQLAP4LIDX", "2Y678X9SU8"),
}

# ===============================================================
# 🧠 Smarter intent detection
# ===============================================================
def detect_intent(user_input: str) -> str:
    text = user_input.lower()

    # Resume intent
    if any(k in text for k in ["resume", "cv", "linkedin", "cover letter", "improve my resume"]):
        return "resume"

    # Project intent
    if any(k in text for k in [
        "project", "portfolio", "build", "create", "make", "ideas", "coding", "develop"
    ]):
        return "project"

    # Course intent
    if any(k in text for k in [
        "course", "class", "take", "learn", "study", "subject", "degree"
    ]):
        return "course"

    # Job intent
    if any(k in text for k in [
        "job", "internship", "career", "position", "opening", "hire", "work"
    ]):
        return "job"

    # Fallback: assume course-related if learning-oriented
    if "learn" in text or "study" in text:
        return "course"

    return "job"

# ===============================================================
# 🧩 Agent invocation
# ===============================================================
def invoke_agent(agent_key: str, prompt: str) -> str:
    agent_id, alias_id = AGENTS[agent_key]
    print(f"→ Invoking {agent_key} agent with prompt: {prompt[:80]}...")

    response = bedrock.invoke_agent(
        agentId=agent_id,
        agentAliasId=alias_id,
        sessionId=f"session-{agent_key}",
        inputText=prompt,
    )

    text = ""
    for event in response.get("completion", []):
        if "chunk" in event and "bytes" in event["chunk"]:
            text += event["chunk"]["bytes"].decode("utf-8", errors="ignore")

    return text.strip() or "(No response generated.)"

# ===============================================================
# 🚀 Lambda entry point
# ===============================================================
def lambda_handler(event, context):
    print("Incoming event:", json.dumps(event))

    # Extract raw input text
    user_input = (
        event.get("goal")
        or event.get("inputText")
        or event.get("parameters", [{}])[0].get("value")
        or "help me find a job"
    ).strip()

    intent = detect_intent(user_input)
    print(f"Detected intent: {intent}")

    # Build more natural prompts
    if intent == "job":
        prompt = f"Find current job or internship opportunities related to {user_input}."
    elif intent == "course":
        prompt = f"Suggest UTD courses that would help someone interested in {user_input}."
    elif intent == "project":
        prompt = f"Generate creative and practical project ideas related to {user_input}."
    elif intent == "resume":
        prompt = f"Provide feedback and suggestions to improve my resume for {user_input}."
    else:
        prompt = f"Help me explore opportunities related to {user_input}."

    output = invoke_agent(intent, prompt)

    return {
        "response": {
            "actionGroup": "CareerMatchingGroup",
            "function": "generate_plan",
            "functionResponse": {
                "responseBody": {"TEXT": {"body": output}}
            },
        }
    }
