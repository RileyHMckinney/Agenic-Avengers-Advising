# server.py
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from tools.tool_wrappers.job_search_tool import JobSearchTool
from agent import agent_handle  # ✅ import your agent

app = FastAPI(title="Agenic Avengers - Agent Backend")

MODE = os.getenv("JOB_TOOL_MODE", "lambda")
LAMBDA_NAME = os.getenv("SERPAPI_LAMBDA_NAME", "serpapi-google-jobs")
REGION = os.getenv("AWS_REGION", "us-east-1")

tool = JobSearchTool(mode=MODE, lambda_name=LAMBDA_NAME, region_name=REGION)

class SearchRequest(BaseModel):
    query: str
    location: Optional[str] = None
    limit: Optional[int] = 10
    next_page_token: Optional[str] = None

@app.post("/api/search")
async def search(req: SearchRequest):
    if not req.query:
        raise HTTPException(status_code=400, detail="query required")
    try:
        result = tool.run(req.query, req.location, req.limit, req.next_page_token)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AgentQuery(BaseModel):
    message: str

@app.post("/api/agent")
def call_agent(query: AgentQuery):
    result = agent_handle(query.message)
    return {"results": result}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
