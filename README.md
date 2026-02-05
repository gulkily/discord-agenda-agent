# Discord Agenda Agent

A Discord community assistant that aggregates **tech events only** from multiple sources (Discord channels, X/Twitter, Luma calendars, and web searches) and automatically posts a formatted agenda to Discord.

## Features

- **Multi-source tech event collection:**
  - Searches Discord channels for community-posted tech events
  - Scans X (Twitter) for tech event announcements
  - Reads calendar events from tech organizations' Luma pages
  - Searches the web for prominent tech events

- **Intelligent compilation:**
  - Filters for tech events only (meetups, conferences, hackathons, workshops, AI/ML events, developer gatherings)
  - Chronologically sorts events
  - Removes duplicates
  - Formats events with all relevant details (time, location, description, registration links)

- **Automatic Discord posting:**
  - Automatically posts compiled agenda to specified Discord channel
  - Handles long messages by splitting into multiple Discord messages (2000 char limit)
  - No user review required - posts immediately after compilation

## Architecture

The project is structured into two main files:

- **`main.py`**: Main agent logic, event collection, agenda compilation, and Discord posting
- **`connection.py`**: DAuth connection schemas for MCP servers (Discord, X/Twitter)

## Prerequisites

1. **Discord App Setup:**
   - Create a Discord app at https://discord.com/developers/docs/intro
   - Obtain your Discord App ID, Token, and Public Key
   - Grant the bot the following scopes:
     - `guilds.channels.read` - To read channel lists
     - `messages.read` - To read messages from channels
     - `Send Messages` - To post the agenda
   - Connect the app to your Discord server

2. **X (Twitter) Bearer Token:**
   - Get a bearer token from https://developer.x.com

3. **Dedalus Labs API Key:**
   - You'll need a Dedalus Labs API key for the agent framework
   - Get it from https://www.dedaluslabs.ai

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd discord-agenda-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `env.example` to `.env`
   - Fill in your credentials:
     ```bash
     # Dedalus API Key
     DEDALUS_API_KEY=your_dedalus_api_key
     DEDALUS_AS_URL=https://as.dedaluslabs.ai

     # Discord Credentials
     DISCORD_APP_ID=your_discord_app_id
     DISCORD_TOKEN=your_discord_token
     DISCORD_PUBLIC_KEY=your_discord_public_key
     
     # Optional: Override default Discord channel for posting
     DISCORD_POST_CHANNEL_ID=your_channel_id

     # X (Twitter) Bearer Token
     X_BEARER_TOKEN=your_x_bearer_token
     ```

## Usage

Run the agent:
```bash
python main.py
```

Or with command-line arguments:
```bash
python main.py "Feb 9th to Feb 15th" "San Francisco"
```

The agent will:
1. Prompt for time frame and location (if not provided as arguments)
2. Search for tech events from all configured sources
3. Compile them into a chronological agenda
4. Display the agenda in the terminal
5. **Automatically post the agenda to Discord** (no user confirmation required)

### Example

```bash
python main.py "next week" "San Francisco"
```

This will:
- Search for tech events in San Francisco for the next week
- Compile the agenda
- Automatically post to the Discord channel specified in `DISCORD_POST_CHANNEL_ID` (or the default channel)

## Event Format

Each event in the agenda follows this format:

```
**Event Title**
Time & Location: [specific time and location]
Description: [1 line description]
Registration: [link when available]
Notes: [special instructions or relevant notes when applicable]
Source: [concise source of information]
```

Events are:
- Sorted chronologically by date and time
- Filtered to include only tech events (meetups, conferences, hackathons, workshops, AI/ML events, developer gatherings)
- Duplicates removed if the same event appears in multiple sources
- Include timezone information when available
- Include registration links whenever available

## Tech Events Focus

The agent **only** searches for and compiles tech-related events:

**Included:**
- Tech meetups, conferences, hackathons, workshops
- Software engineering, programming, AI/ML, data science events
- Startup events, tech networking, developer gatherings
- Tech talks, seminars, webinars

**Excluded:**
- Music, art, sports events
- General social gatherings (unless tech-related)
- Non-tech community events

## MCP Servers

The agent uses the following MCP (Model Context Protocol) servers:

- **`nickyhec/discord-mcp`** - Discord channel searches and message reading
- **`windsor/x-api-mcp`** - X/Twitter API integration for event searches
- **`tsion/brave-search-mcp`** - Web searches and Luma calendar access

MCP servers read credentials directly from environment variables (no DAuth credentials need to be passed).

## Models

The agent uses multiple models for different tasks:

- **`anthropic/claude-opus-4-5`** - Event search and collection
- **`openai/gpt-4-turbo`** - Agenda compilation and formatting

## How It Works

1. **Event Collection**: The agent searches multiple sources simultaneously:
   - Discord channels in the specified server (searches channels like #events, #announcements, #social, #general)
   - X/Twitter for tech event announcements
   - Luma calendars for tech organizations
   - Web searches for prominent tech events

2. **Agenda Compilation**: Events are:
   - Filtered to include only tech events
   - Sorted chronologically
   - Deduplicated
   - Formatted according to the specified format

3. **Discord Posting**: After compilation:
   - The agenda is captured via the `capture_agenda` tool
   - Python code automatically posts to Discord
   - Long agendas are split into multiple messages (Discord 2000 character limit)
   - Posts to the channel specified in `DISCORD_POST_CHANNEL_ID` environment variable

## Project Structure

```
discord-agenda-agent/
├── main.py              # Main agent logic and Discord posting
├── connection.py        # DAuth connection schemas for MCP servers
├── requirements.txt     # Python dependencies
├── env.example         # Environment variable template
├── .env                # Your actual credentials (not in git)
└── README.md           # This file
```

## Error Handling

The agent handles various error scenarios:

- **Discord authentication errors**: Displays clear error messages
- **Missing permissions**: Indicates which Discord scopes are needed
- **No events found**: Includes "No posted Discord tech community events" in the agenda
- **Posting failures**: Logs detailed error information with HTTP status and response body

## Troubleshooting

**Agent doesn't post to Discord:**
- Check that `DISCORD_TOKEN` is set correctly in `.env`
- Verify the bot has `Send Messages` permission in the target channel
- Check that `DISCORD_POST_CHANNEL_ID` is set to a valid channel ID

**No events found:**
- Verify Discord bot has `guilds.channels.read` and `messages.read` scopes
- Check that the bot is a member of the Discord server
- Ensure the time frame and location parameters are clear

**X/Twitter search not working:**
- Verify `X_BEARER_TOKEN` is set correctly
- Check that the token has the necessary permissions

## License

See LICENSE file for details.
