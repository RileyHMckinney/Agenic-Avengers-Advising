import json
import boto3
import base64
from io import BytesIO
from PyPDF2 import PdfReader

# Initialize Bedrock client globally for efficiency
bedrock = boto3.client("bedrock-agent-runtime")


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text from a PDF file using PyPDF2 (Lambda layer provided)."""
    text = ""
    try:
        reader = PdfReader(BytesIO(file_bytes))
        for page in reader.pages:
            if page_text := page.extract_text():
                text += page_text + "\n"
    except Exception as e:
        text = f"[PDF extraction failed: {e}]"
    return text.strip()


def get_cors_headers(event):
    """Return dynamic CORS headers based on the incoming request origin."""
    origin = event.get("headers", {}).get("origin", "")
    allowed_origins = [
        "http://localhost:3000",
        "https://main.du0i05f4q84fg.amplifyapp.com",
        "https://eidaadvisor.com",
        "https://www.eidaadvisor.com"
    ]
    allow_origin = origin if origin in allowed_origins else "https://main.du0i05f4q84fg.amplifyapp.com"

    return {
        "Access-Control-Allow-Origin": allow_origin,
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST,OPTIONS",
        "Access-Control-Allow-Credentials": "true",
        "Content-Type": "application/json",
    }


def lambda_handler(event, context):
    try:
        print("Incoming event keys:", list(event.keys()))

        cors_headers = get_cors_headers(event)

        # === Handle CORS preflight ===
        if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": cors_headers,
                "body": json.dumps({"message": "CORS preflight OK"}),
            }

        user_message = ""
        pdf_text = ""

        # Normalize headers
        headers = {k.lower(): v for k, v in event.get("headers", {}).items()} if event.get("headers") else {}
        content_type = headers.get("content-type", "")

        # === CASE 1: JSON input (regular chat) ===
        if "application/json" in content_type:
            body = json.loads(event.get("body", "{}") or "{}")
            user_message = body.get("message", "").strip()

        # === CASE 2: Multipart form-data (PDF upload + message) ===
        elif "multipart/form-data" in content_type:
            boundary = content_type.split("boundary=")[-1]
            body_bytes = base64.b64decode(event["body"]) if event.get("isBase64Encoded") else event["body"].encode()

            for part in body_bytes.split(f"--{boundary}".encode()):
                if b'name="message"' in part:
                    start = part.find(b"\r\n\r\n") + 4
                    user_message = part[start:].strip().decode("utf-8", errors="ignore")
                elif b'name="file"' in part:
                    start = part.find(b"\r\n\r\n") + 4
                    file_bytes = part[start:].strip()
                    pdf_text = extract_text_from_pdf(file_bytes)

        else:
            print(f"❌ Unsupported content type: {content_type}")
            return {
                "statusCode": 400,
                "headers": cors_headers,
                "body": json.dumps({"error": "Unsupported content type."}),
            }

        # Combine message + resume context
        combined_input = user_message
        if pdf_text:
            combined_input += "\n\nHere is the text extracted from the attached resume:\n" + pdf_text[:6000]

        if not combined_input.strip():
            return {
                "statusCode": 400,
                "headers": cors_headers,
                "body": json.dumps({"error": "Empty input."}),
            }

        print(f"🧠 Sending to Claude (first 200 chars): {combined_input[:200]}")

        # === Bedrock Agent Invocation ===
        try:
            response = bedrock.invoke_agent(
                agentId="JGTQXH9PYU",
                agentAliasId="WTUG4HEFOY",
                sessionId="frontend-session",
                inputText=combined_input,
            )
        except Exception as invoke_error:
            print("❌ Bedrock invocation failed:", invoke_error)
            return {
                "statusCode": 502,
                "headers": cors_headers,
                "body": json.dumps({"error": f"Bedrock invocation failed: {str(invoke_error)}"}),
            }

        # === Parse Response ===
        output_text = ""

        if "completion" in response:
            for event_piece in response.get("completion", []):
                if "chunk" in event_piece and "bytes" in event_piece["chunk"]:
                    output_text += event_piece["chunk"]["bytes"].decode("utf-8", errors="ignore")

        if not output_text.strip():
            if "outputText" in response:
                output_text = response["outputText"]
            elif "sessionState" in response and "returnText" in response["sessionState"]:
                output_text = response["sessionState"]["returnText"]
            else:
                output_text = json.dumps(response, indent=2)[:6000]

        print("✅ Response length:", len(output_text))

        # === Success Response ===
        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps({"reply": output_text.strip()}),
        }

    except Exception as e:
        print("❌ Unhandled Exception:", str(e))
        return {
            "statusCode": 500,
            "headers": get_cors_headers(event),
            "body": json.dumps({"error": str(e)}),
        }
