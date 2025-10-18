import boto3
import json
from typing import Optional, Dict, Any

class MemoryTool:
    def __init__(self, region: str = "us-east-1"):
        self.dynamo = boto3.client("dynamodb", region_name=region)
        self.table_name = "AgenicUserMemory"

    def save_memory(self, user_id: str, data: Dict[str, Any]):
        self.dynamo.put_item(
            TableName=self.table_name,
            Item={
                "user_id": {"S": user_id},
                "data": {"S": json.dumps(data)}
            }
        )

    def load_memory(self, user_id: str) -> Optional[Dict[str, Any]]:
        response = self.dynamo.get_item(
            TableName=self.table_name,
            Key={"user_id": {"S": user_id}}
        )
        item = response.get("Item")
        if not item:
            return None
        return json.loads(item["data"]["S"])
