import boto3
import json

# Initialize the Bedrock runtime client
client = boto3.client("bedrock-runtime", region_name="us-east-1")

def invoke_bedrock(prompt):
    # Claude models require this "anthropic_version" field
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "temperature": 0.7,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    })

    response = client.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",  # Claude 3.5 Sonnet
        body=body
    )

    result = json.loads(response["body"].read())
    print("\nMODEL RESPONSE:\n", result["content"][0]["text"])

if __name__ == "__main__":
    invoke_bedrock("Write a one-sentence mission statement for the Agenic Avengers Advising Agent.")
