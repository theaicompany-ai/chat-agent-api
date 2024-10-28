# ... existing imports ...
from openai_swarm import Tool

# ... existing helper functions ...

def initialize_tools():
    tool1 = Tool(name="tool_name_1", endpoint="https://api.tool1.com")
    tool2 = Tool(name="tool_name_2", endpoint="https://api.tool2.com")
    return [tool1, tool2]

# ... existing helper functions ...

