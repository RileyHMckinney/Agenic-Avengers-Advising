import os
from tools.tool_wrappers.job_search_tool import JobSearchTool

# initialize tool
job_tool = JobSearchTool(
    mode=os.getenv("JOB_TOOL_MODE", "local"),
    lambda_name=os.getenv("SERPAPI_LAMBDA_NAME", "serpapi-google-jobs"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

def agent_handle(user_message: str):
    """Basic agent that routes to tools."""
    msg_lower = user_message.lower()
    if "job" in msg_lower or "intern" in msg_lower:
        query = user_message
        results = job_tool.run(query=query, location=None, limit=3)
        return format_results(results)
    else:
        return "I'm here to help with job searches. Try asking: find software engineer internships."

def format_results(results):
    if not results or "results" not in results:
        return "No jobs found."

    job_list = results["results"]
    formatted = []

    for job in job_list[:5]:  # show top 5 jobs
        title = job.get("title", "Untitled")
        company = job.get("company", "Unknown")
        location = job.get("location", "N/A")
        link = job.get("link", "")
        formatted.append(f"**{title}** — {company} ({location})\n{link}")

    return "\n\n".join(formatted)
