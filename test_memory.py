from tools.tool_wrappers.memory_tool import MemoryTool

memory = MemoryTool(region="us-east-1")

user_id = "test_user"
memory.save_memory(user_id, {"skills": ["Python", "AWS"], "last_query": "software engineer intern"})
print("Saved memory successfully.")

loaded = memory.load_memory(user_id)
print("Loaded memory:", loaded)
