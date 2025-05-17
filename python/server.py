from mcp.server.fastmcp import FastMCP
from dogfighters.dogfight import Dogfight

# Initialize the FastMCP server with a name
mcp = FastMCP("dogfight")

# Define a simple tool that returns a dummy response
@mcp.tool()
async def hello_world(name: str = "World") -> str:
    """
    A simple hello world function that returns a greeting.
    
    Args:
        name: The name to greet (default: "World")
    """
    return f"Hello, {name}! This is the Dogfight MCP server."

@mcp.tool()
async def debate(problem: str, max_rounds: int = 3) -> str:
    """
    Runs a dogfight to generate a solution for the given problem.
    """
    actors = {
        "Security Engineer": "security, compliance.",
        "Performance Engineer": "performance, scalability.",
        "ML Engineer": "machine learning, algorithms.",
        "Data Engineer": "data management, analytics.",
    }
    dogfight = Dogfight(actors, max_rounds=max_rounds, consensus_threshold=0.8)
    proposal = dogfight.debate(problem)
    return proposal

# Run the server when this script is executed directly
if __name__ == "__main__":
    # Start the server
    print("Starting minimal Dogfight MCP Server...")
    # For Claude Desktop, we need to use stdio transport
    mcp.run(transport="stdio")
