"""
Exposes CodeSentinel's static-analysis and RAG-search capabilities as an
MCP server, so the same tools used internally by the agent graph can be
called by any MCP-compatible client (IDE assistants, other agents).
Run with: `python -m app.mcp.mcp_server`
"""
import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from app.mcp.mcp_tools import tool_run_static_analysis, tool_search_codebase

server = Server("codesentinel-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="run_static_analysis",
            description="Run Semgrep, Bandit and ESLint against a set of files and return normalized findings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target_dir": {"type": "string"},
                    "changed_files": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["target_dir", "changed_files"],
            },
        ),
        Tool(
            name="search_codebase",
            description="Semantic search over an indexed repository's code using pgvector.",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_id": {"type": "string"},
                    "query": {"type": "string"},
                    "top_k": {"type": "integer", "default": 5},
                },
                "required": ["repository_id", "query"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "run_static_analysis":
        result = await tool_run_static_analysis(arguments["target_dir"], arguments["changed_files"])
    elif name == "search_codebase":
        result = await tool_search_codebase(
            arguments["repository_id"], arguments["query"], arguments.get("top_k", 5)
        )
    else:
        raise ValueError(f"Unknown tool: {name}")
    return [TextContent(type="text", text=str(result))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
