"""Connection configuration for MCP servers."""
import os
from dotenv import load_dotenv

load_dotenv()


def check_discord_credentials() -> bool:
    """Checks if Discord credentials are available and prints status."""
    token = os.getenv("DISCORD_TOKEN", "")
    app_id = os.getenv("DISCORD_APP_ID", "")
    
    if not token:
        print("⚠️  DISCORD_TOKEN not found. Discord access may fail.", flush=True)
        return False
    print(f"✓ Discord token found (App ID: {app_id or 'N/A'})", flush=True)
    return True
