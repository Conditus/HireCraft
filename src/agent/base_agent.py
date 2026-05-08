# Just sketch of an agent (don't rly know what for btw)

from src.agent.kit import get_tools, get_tools_description
import json

class agent:
    def __init__(self):
        # Tools
        self.tools = get_tools()
        self.tools_description = json.loads(get_tools_description())