"""
Connection configuration for MCP servers.
Defines Connection schemas and binds credentials using SecretValues.
"""
import os
from dedalus_mcp.auth import Connection, SecretKeys, SecretValues
from dotenv import load_dotenv

load_dotenv()


def get_discord_mcp_connection():
    """
    Creates and returns Discord MCP connection with bound credentials.
    
    Returns:
        SecretValues: Discord MCP credentials bound to connection schema
    """
    # DAuth connection to Discord MCP
    # Connection: schema for Discord MCP server
    # Note: The discord-mcp server uses "Bot {token}" format for Discord API calls
    # The Connection class requires {api_key} placeholder, which will be replaced with the token
    discord_mcp_connection = Connection(
        name="discord-mcp",
        secrets=SecretKeys(
            discord_app_id="DISCORD_APP_ID",
            discord_token="DISCORD_TOKEN",
            discord_public_key="DISCORD_PUBLIC_KEY"
        ),
        base_url="https://discord.com/api/v9",
        auth_header_format="Bot {api_key}",
    )
    
    # SecretValues: binds actual Discord credentials to a Connection schema.
    # Encrypted client-side, decrypted in secure enclave at dispatch time.
    discord_mcp_secrets = SecretValues(
        discord_mcp_connection,
        discord_app_id=os.getenv("DISCORD_APP_ID", ""),
        discord_token=os.getenv("DISCORD_TOKEN", ""),
        discord_public_key=os.getenv("DISCORD_PUBLIC_KEY", "")
    )
    
    return discord_mcp_secrets


def get_x_connection():
    """
    Creates and returns X (Twitter) API connection with bound credentials.
    
    Returns:
        SecretValues: X API credentials bound to connection schema
    """
    # DAuth connection to X
    # Connection: schema for X/Twitter API
    x_connection = Connection(
        name="x",
        secrets=SecretKeys(token="X_BEARER_TOKEN"),
        base_url="https://api.x.com",
        auth_header_format="Bearer {api_key}",
    )

    # SecretValues: binds actual credentials to a Connection schema.
    # Encrypted client-side, decrypted in secure enclave at dispatch time.
    x_secrets = SecretValues(x_connection, token=os.getenv("X_BEARER_TOKEN", ""))
    
    return x_secrets


def get_all_credentials():
    """
    Gets all available credentials for MCP servers.
    
    Returns:
        list: List of JSON-serializable credential dicts for available credentials
    """
    credentials_list = []
    
    # Add Discord MCP credentials if available
    discord_token = os.getenv("DISCORD_TOKEN", "")
    if discord_token:
        try:
            discord_secrets = get_discord_mcp_connection()
            # Convert SecretValues to JSON-serializable dict
            # Try Pydantic v2 method first, fallback to v1
            if hasattr(discord_secrets, 'model_dump'):
                credentials_list.append(discord_secrets.model_dump())
            elif hasattr(discord_secrets, 'dict'):
                credentials_list.append(discord_secrets.dict())
            else:
                # Fallback: create dict manually
                credentials_list.append({
                    "name": "discord-mcp",
                    "secrets": {
                        "discord_app_id": os.getenv("DISCORD_APP_ID", ""),
                        "discord_token": os.getenv("DISCORD_TOKEN", ""),
                        "discord_public_key": os.getenv("DISCORD_PUBLIC_KEY", "")
                    }
                })
        except Exception as e:
            print(f"Warning: Could not add Discord MCP credentials: {e}", flush=True)
    
    # Add X credentials if available
    x_token = os.getenv("X_BEARER_TOKEN", "")
    if x_token:
        try:
            x_secrets = get_x_connection()
            # Convert SecretValues to JSON-serializable dict
            if hasattr(x_secrets, 'model_dump'):
                credentials_list.append(x_secrets.model_dump())
            elif hasattr(x_secrets, 'dict'):
                credentials_list.append(x_secrets.dict())
            else:
                # Fallback: create dict manually
                credentials_list.append({
                    "name": "x",
                    "secrets": {
                        "token": os.getenv("X_BEARER_TOKEN", "")
                    }
                })
        except Exception as e:
            print(f"Warning: Could not add X credentials: {e}", flush=True)
    
    return credentials_list


def check_discord_credentials():
    """
    Checks if Discord credentials are available and prints status.
    """
    discord_token = os.getenv("DISCORD_TOKEN", "")
    discord_app_id = os.getenv("DISCORD_APP_ID", "")
    
    if not discord_token:
        print("⚠️  Warning: DISCORD_TOKEN not found in environment variables.", flush=True)
        print("   The discord-mcp server may not be able to authenticate to Discord.", flush=True)
        print("   Discord channel access may fail. Make sure DISCORD_TOKEN is set in .env", flush=True)
        return False
    else:
        print(f"✓ Discord token found (App ID: {discord_app_id or 'N/A'})", flush=True)
        return True
