# Discord Agenda Agent

A Discord bot that aggregates **tech events only** from multiple sources (Discord channels, X/Twitter, and web searches) and automatically posts a formatted agenda to Discord.

## Features

- **Multi-source tech event collection:**
  - Reads Discord channels for community-posted tech events
  - Searches X/Twitter influencers for tech event announcements
  - Searches the web for Luma calendars, hackathons, and tech meetups

- **Intelligent filtering:**
  - Filters for tech events only (meetups, conferences, hackathons, workshops, AI/ML events, developer gatherings)
  - Excludes non-tech events (music, art, sports, general social events)
  - Formats events with all relevant details (time, location, description, registration links)

- **Automatic Discord posting:**
  - Posts compiled agenda to specified Discord channel
  - Handles long messages by splitting into multiple Discord messages (2000 char limit)
  - Streams agent output in real-time

## Architecture

```
discord-agenda-agent/
├── main.py              # Agent logic, streaming, and Discord posting
├── connection.py        # DAuth connection schemas for MCP servers
├── requirements.txt     # Python dependencies
├── env.example          # Environment variable template
├── .env                 # Your credentials (not in git)
└── README.md
```

## Prerequisites

1. **Discord Bot Setup:**
   - Create a Discord app at https://discord.com/developers/applications
   - Create a bot and get the bot token
   - Grant the bot these permissions:
     - `Read Messages/View Channels` - To read channel lists
     - `Read Message History` - To read messages from channels
     - `Send Messages` - To post the agenda
   - Invite the bot to your Discord server

2. **X (Twitter) Bearer Token:**
   - Get a bearer token from https://developer.x.com

3. **Dedalus Labs API Key:**
   - Get an API key from https://www.dedaluslabs.ai

## Installation

1. Clone this repository:
```bash
git clone https://github.com/NickyHeC/discord-agenda-agent.git
cd discord-agenda-agent
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp env.example .env
```

Edit `.env` with your credentials:
```bash
# Dedalus API Key
DEDALUS_API_KEY=your_dedalus_api_key
DEDALUS_AS_URL=https://as.dedaluslabs.ai

# Discord Credentials
DISCORD_TOKEN=your_discord_bot_token
DISCORD_GUILD_ID=your_discord_server_id
DISCORD_POST_CHANNEL_ID=your_target_channel_id

# X (Twitter) API
X_BEARER_TOKEN=your_x_bearer_token
```

## Usage

Run the agent with command-line arguments:
```bash
python main.py "next week" "San Francisco"
```

Or run interactively:
```bash
python main.py
# Prompts for time frame and location
```

The agent will:
1. Search for tech events from Discord, X/Twitter, and web sources
2. Stream the results in real-time to your terminal
3. Automatically post the compiled agenda to Discord

## How It Works

1. **Event Collection**: The agent searches multiple sources:
   - **Discord**: Reads channels from the specified guild (server) for event announcements
   - **X/Twitter**: Finds tech influencers via web search, then searches their recent tweets
   - **Web**: Searches for Luma calendars, hackathons, and tech meetups

2. **Streaming Output**: Results stream to your terminal as the agent works

3. **Discord Posting**: The compiled agenda is:
   - Formatted with a header and timestamp
   - Split into multiple messages if over 2000 characters
   - Posted to the channel specified in `DISCORD_POST_CHANNEL_ID`

## MCP Servers

The agent uses these MCP (Model Context Protocol) servers via Dedalus Labs:

| Server | Purpose |
|--------|---------|
| `nickyhec/discord-mcp` | Discord channel reading and message access |
| `windsor/x-api-mcp` | X/Twitter API for searching user tweets |
| `tsion/brave-search-mcp` | Web searches for events and calendars |

Credentials are passed securely via DAuth (encrypted client-side, decrypted in secure enclave).

## Event Format

Each event in the agenda follows this format:

```
**Event Title**
Time & Location: [specific time and location]
Description: [1 line description]
Registration: [link]
Source: [source]
```

## Tech Events Focus

**Included:**
- Tech meetups, conferences, hackathons, workshops
- AI/ML, data science, programming events
- Startup events, tech networking, developer gatherings

**Excluded:**
- Music, art, sports events
- General social gatherings (unless tech-related)

## Troubleshooting

**Agent doesn't post to Discord:**
- Check that `DISCORD_TOKEN` is set correctly
- Verify `DISCORD_POST_CHANNEL_ID` is a valid channel ID
- Ensure the bot has `Send Messages` permission in that channel

**Discord channel reading fails:**
- Verify `DISCORD_GUILD_ID` is correct (right-click server → Copy Server ID)
- Check the bot is a member of the server
- Ensure the bot has `Read Messages` and `Read Message History` permissions

**X/Twitter returns no results:**
- This often means no matching tweets were found (not an error)
- The agent will note "X unavailable" and continue with other sources

**No events found:**
- Try broadening the time frame or location
- Check the event calendars linked in the output for real-time updates

## License

See LICENSE file for details.
