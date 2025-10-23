import json
import boto3
import uuid
import base64
import io
from PyPDF2 import PdfReader

# AWS Clients
s3 = boto3.client("s3")
bedrock_agent = boto3.client("bedrock-agent-runtime")

# === CONFIGURATION ===
BUCKET_NAME = "jobmarket-agent-knowledge"     # S3 bucket
KNOWLEDGE_BASE_ID = "LZYESBWUB7"              # Bedrock KB ID
RESUME_DATASOURCE_ID = "DS67890XYZ"           # <-- Replace with the real Data Source ID for /resumes/


# === PDF Extraction ===
def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text from a PDF file (bytes)."""
    text = ""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        text = f"[PDF extraction failed: {e}]"
    return text.strip()


# === Main Lambda Entry Point ===
def lambda_handler(event, context):
    """Entry point for Bedrock Agent integration (handles both upload + retrieval)."""
    try:
        print("Incoming event:", json.dumps(event)[:1500])

        # Bedrock Agent parameters (these vary depending on invocation type)
        params = event.get("parameters", {}) or event.get("requestBody", {}) or {}
        input_text = event.get("inputText", "").lower()

        resume_text = params.get("resume_text")
        file_name = params.get("file_name", "")
        file_content = params.get("file_content")

        # 1️⃣ --- File Upload Path ---
        if file_content:
            print("🧾 Detected uploaded file. Processing resume upload...")
            resume_text = handle_resume_upload(file_name, file_content)
            return format_response(
                200,
                {"message": "Resume uploaded and indexed successfully.", "characters": len(resume_text)}
            )

        # 2️⃣ --- Resume Retrieval Path ---
        elif "resume" in input_text:
            # Extract likely name to search for (naive name check for now)
            if "riley" in input_text:
                query_text = "riley mckinney resume"
            else:
                query_text = "resume"

            print(f"📚 Searching KB for: {query_text}")
            kb_results = query_knowledge_base(query_text)
            return format_response(200, {"message": "Resume lookup complete.", "results": kb_results})

        # 3️⃣ --- Fallback: Nothing Provided ---
        else:
            print("⚠️ No resume file or identifiable name found.")
            return format_response(400, {"error": "No resume provided or identifiable name found."})

    except Exception as e:
        print("❌ Error:", str(e))
        return format_response(500, {"error": str(e)})


# === Resume Upload Handler ===
def handle_resume_upload(file_name: str, file_content: str) -> str:
    """Decode, extract, upload to S3, and start Knowledge Base ingestion."""
    raw_bytes = base64.b64decode(file_content)

    # Extract text from PDF
    if file_name.lower().endswith(".pdf"):
        resume_text = extract_text_from_pdf(raw_bytes)
    else:
        raise ValueError("Unsupported file type. Only PDF supported.")

    # Upload structured record to S3
    key = f"resumes/{uuid.uuid4()}.json"
    record = {"file_name": file_name, "resume_text": resume_text}

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json.dumps(record, indent=2),
        ContentType="application/json"
    )
    print(f"✅ Uploaded resume to s3://{BUCKET_NAME}/{key}")

    # Trigger targeted ingestion for resumes only
    try:
        ingest_response = bedrock_agent.start_ingestion_job(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            dataSourceId=RESUME_DATASOURCE_ID,
            description=f"Ingest resume {key}"
        )
        print("📥 Resume ingestion job started:", json.dumps(ingest_response, indent=2)[:800])
    except Exception as e:
        print("⚠️ Knowledge Base ingestion failed:", str(e))
        raise

    return resume_text


# === Resume Retrieval Handler ===
def query_knowledge_base(query: str) -> dict:
    """Query the Bedrock Knowledge Base for resumes (restricted to /resumes/ data source)."""
    try:
        response = bedrock_agent.retrieve(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            retrievalQuery={"text": query},
            retrievalConfiguration={
                "vectorSearchConfiguration": {
                    "numberOfResults": 3,
                    "filter": {
                        "equals": {
                            "key": "dataSourceId",
                            "value": RESUME_DATASOURCE_ID
                        }
                    }
                }
            }
        )

        print("📖 KB query response:", json.dumps(response)[:800])

        results = []
        for doc in response.get("retrievalResults", []):
            results.append({
                "documentId": doc.get("documentId"),
                "content": doc.get("content"),
                "score": doc.get("score")
            })

        return results or {"message": "No resumes found in the knowledge base."}

    except Exception as e:
        print("⚠️ KB retrieval error:", str(e))
        return {"error": str(e)}

# === Bedrock Agent Response Formatter ===
def format_response(status_code: int, body: dict) -> dict:
    """Format response in the exact structure Bedrock expects."""
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": "resumeStorage",
            "apiPath": "/store_resume",
            "httpMethod": "POST",
            "httpStatusCode": status_code,
            "responseBody": {
                "application/json": {
                    "body": body
                }
            }
        }
    }
