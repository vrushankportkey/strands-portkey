"""
Strands Agent with Portkey integration and multiple MCP servers.
Supports:
- Linear MCP (via Portkey API key)
- GitHub MCP (via GitHub PAT)
"""

import os
import sys

# Configuration
PORTKEY_API_KEY = os.environ.get("PORTKEY_API_KEY", "")
GITHUB_PAT = os.environ.get("GITHUB_PAT", "")
MODEL_SLUG = "@anthropic/claude-sonnet-4-5"
LINEAR_MCP_URL = os.environ.get("LINEAR_MCP_URL", "")
GITHUB_MCP_URL = os.environ.get("GITHUB_MCP_URL", "")


def main():
    """Run interactive Strands Agent with multiple MCP tools via Portkey."""
    print("\n🔮 Initializing Strands Agent...")
    print("  • Loading dependencies (this may take a moment)...")
    
    # Lazy import heavy dependencies to show feedback immediately
    from strands import Agent
    from strands.models.openai import OpenAIModel
    from strands.tools.mcp import MCPClient
    from mcp.client.streamable_http import streamablehttp_client
    from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders

    def create_model():
        """Create an OpenAI model configured to use Portkey gateway."""
        if not PORTKEY_API_KEY:
            raise ValueError("PORTKEY_API_KEY environment variable is required")
        
        return OpenAIModel(
            client_args={
                "api_key": PORTKEY_API_KEY,
                "base_url": PORTKEY_GATEWAY_URL,
                "default_headers": createHeaders(
                    trace_id="strands-multi-mcp-agent",
                    metadata={
                        "agent_type": "multi-mcp-integration",
                        "framework": "strands-agents"
                    }
                )
            },
            model_id=MODEL_SLUG,
            params={
                "max_tokens": 4096,
                "temperature": 0.7,
            }
        )

    def create_linear_mcp_transport():
        """Create MCP transport for Linear server with Portkey auth."""
        return streamablehttp_client(
            url=LINEAR_MCP_URL,
            headers={
                "x-portkey-api-key": PORTKEY_API_KEY
            }
        )

    def create_github_mcp_transport():
        """Create MCP transport for GitHub server (via Portkey with PAT forwarding)."""
        return streamablehttp_client(
            url=GITHUB_MCP_URL,
            headers={
                "x-portkey-api-key": PORTKEY_API_KEY,
                "Authorization": f"Bearer {GITHUB_PAT}"
            }
        )

    print("  • Connecting to Portkey Gateway...")
    model = create_model()
    
    # Build list of MCP clients based on available config
    mcp_clients = []
    
    # Linear MCP (always available if Portkey key is set)
    print("  • Connecting to Linear MCP...")
    linear_mcp = MCPClient(
        transport_callable=create_linear_mcp_transport,
        prefix="linear"  # Tools become linear_list_issues, etc.
    )
    mcp_clients.append(linear_mcp)
    
    # GitHub MCP (optional, requires GITHUB_PAT and GITHUB_MCP_URL)
    github_mcp = None
    if GITHUB_PAT and GITHUB_MCP_URL:
        print("  • Connecting to GitHub MCP...")
        github_mcp = MCPClient(
            transport_callable=create_github_mcp_transport,
            prefix="github"  # Tools become github_list_issues, etc.
        )
        mcp_clients.append(github_mcp)
    
    # Create agent with all MCP tools
    print("  • Configuring Agent tools...")
    agent = Agent(model=model, tools=mcp_clients)
    
    print("  ✅ Ready!\n")
    print("=" * 60)
    print("🚀 Multi-Tool Agent (powered by Strands + Portkey)")
    print("=" * 60)
    print("Connected services:")
    print("  ✅ Linear (project management)")
    if github_mcp:
        print("  ✅ GitHub (code & repos)")
    else:
        print("  ⏸️  GitHub (set GITHUB_PAT and GITHUB_MCP_URL to enable)")
    print("\nType 'quit' or 'exit' to end the session.\n")
    
    try:
        while True:
            try:
                user_input = input("\n📝 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ('quit', 'exit', 'q'):
                    print("\n👋 Goodbye!")
                    os._exit(0)
                
                print("\n🤖 Agent:")
                response = agent(user_input)
                print(f"\n{response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    finally:
        # Properly close all MCP client connections
        for client in mcp_clients:
            try:
                client.stop()
            except Exception:
                pass


if __name__ == "__main__":
    main()
