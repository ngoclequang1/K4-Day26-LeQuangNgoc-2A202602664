"""
Weather Agent - Connects to Remote MCP Server on Cloud Run
Successfully connects to custom MCP HTTP endpoints!
"""
import truststore

# Use the Windows certificate store before importing network clients from ADK.
truststore.inject_into_ssl()

from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams
from dotenv import load_dotenv
import logging
import os

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mặc định: server chạy local. Deploy lên Cloud Run thì đặt MCP_SERVER_URL trong .env
# (ví dụ: https://<service>.run.app/mcp). verify_setup.py đọc cùng biến này.
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8085/mcp")

logger.info("Initializing weather agent with remote MCP server")
logger.info("MCP Server: %s", MCP_SERVER_URL)

try:
    # Create connection parameters for the remote MCP server
    connection_params = StreamableHTTPConnectionParams(
        url=MCP_SERVER_URL,
        timeout=30.0,  # Increased timeout for Cloud Run cold starts
    )
    
    # Create the MCP toolset - this will connect to the remote server
    logger.info("Configuring MCP connection...")
    weather_tools = McpToolset(
        connection_params=connection_params,
    )
    logger.info("MCP toolset created successfully")
    
    # Create the agent with remote MCP tools
    root_agent = Agent(
        name="weather_agent",
        model="gemini-2.5-flash",
        description="An assistant that provides current weather and 1-3 day forecasts.",
        instruction=(
            "Use the MCP weather tools for weather questions. Never invent live "
            "conditions. Ask for a city when it is missing, and keep forecast "
            "requests between 1 and 3 days."
        ),
        tools=[weather_tools],
    )
    logger.info("Weather agent initialized with remote MCP tools:")
    logger.info("   - get_current_weather(city)")
    logger.info("   - get_forecast(city, days)")
    logger.info("   - health_check()")
    logger.info("MCP connection will be opened when the agent uses its tools")
    
except Exception as e:
    logger.error("Failed to configure remote MCP server: %s", e)
    logger.error(f"   Server URL: {MCP_SERVER_URL}")
    import traceback
    traceback.print_exc()
    
    # Create a fallback agent without tools
    logger.warning("Creating fallback agent without MCP tools")
    root_agent = Agent(
        name="weather_agent",
        model="gemini-2.5-flash",
        description="Weather assistant (MCP tools unavailable).",
        instruction=(
            "Explain that live weather tools are currently unavailable and do not "
            "invent weather data. Ask the user to check the MCP server connection."
        ),
    )

