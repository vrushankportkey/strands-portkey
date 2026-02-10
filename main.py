"""
Strands Agent with Portkey integration and MCP server.
"""

import os
import sys

# Configuration
PORTKEY_API_KEY = os.environ.get("PORTKEY_API_KEY", "")
MCP_API_KEY = os.environ.get("MCP_API_KEY", "")
MODEL_SLUG = "@anthropic/claude-sonnet-4-5"
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "")


def main():
    """Run interactive Strands Agent with MCP tools via Portkey."""
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
                    trace_id="strands-mcp-agent",
                    metadata={
                        "agent_type": "mcp-integration",
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

    def create_mcp_transport():
        """Create MCP transport via Portkey with auth forwarding."""
        return streamablehttp_client(
            url=MCP_SERVER_URL,
            headers={
                "x-portkey-api-key": PORTKEY_API_KEY,
                "Authorization": f"Bearer {MCP_API_KEY}"
            }
        )

    print("  • Connecting to Portkey Gateway...")
    model = create_model()
    
    print("  • Connecting to MCP server...")
    mcp_client = MCPClient(
        transport_callable=create_mcp_transport
    )
    
    print("  • Configuring Agent tools...")
    agent = Agent(model=model, tools=[mcp_client])
    
    print("  ✅ Ready!\n")
    print("=" * 60)
    print("🚀 Strands Agent (powered by Portkey)")
    print("=" * 60)
    print(f"Connected to: {MCP_SERVER_URL}")
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
        try:
            mcp_client.stop()
        except Exception:
            pass


if __name__ == "__main__":
    main()
