"""Connection configuration for MCP servers."""
import os
from dedalus_mcp.auth import Connection, SecretKeys, SecretValues
from dotenv import load_dotenv

load_dotenv()

# X API MCP Connection
x = Connection(
    name="x",
    secrets=SecretKeys(token="X_BEARER_TOKEN"),
    base_url="https://api.x.com",
)

# Encrypted client-side, decrypted in secure enclave at dispatch time.
x_secrets = SecretValues(x, token=os.getenv("X_BEARER_TOKEN", ""))

discord = Connection(
    name="discord",  # MUST match server Connection name
    secrets=SecretKeys(token="DISCORD_TOKEN"),
    base_url="https://discord.com/api/v9",
    auth_header_format="Bot {api_key}",
)

discord_secrets = SecretValues(discord, token=os.getenv("DISCORD_TOKEN", ""))
