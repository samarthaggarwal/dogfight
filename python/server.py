from mcp.server.fastmcp import FastMCP

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

# Run the server when this script is executed directly
if __name__ == "__main__":
    # Start the server
    print("Starting minimal Dogfight MCP Server...")
    # For Claude Desktop, we need to use stdio transport
    mcp.run(transport="stdio")
