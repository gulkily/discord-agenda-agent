"""Discord Agenda Agent - Collects tech events and posts to Discord."""
import os
import sys
import asyncio
import httpx
from datetime import datetime
from dedalus_labs import AsyncDedalus, DedalusRunner
# from dedalus_labs.utils.stream import stream_async
from dotenv import load_dotenv
from connection import x_secrets, discord_secrets

load_dotenv()

DISCORD_API = "https://discord.com/api/v9"
DISCORD_MAX = 2000


def chunk(text: str, limit: int = DISCORD_MAX) -> list[str]:
    """Split text into chunks that fit Discord's 2000 char limit, preserving line breaks."""
    if len(text) <= limit:
        return [text] if text else [""]
    
    chunks, current = [], ""
    for line in text.splitlines(keepends=True):
        # Handle lines longer than the limit
        while len(line) > limit:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(line[:limit])
            line = line[limit:]
        
        if len(current) + len(line) <= limit:
            current += line
        else:
            if current:
                chunks.append(current)
            current = line
    
    if current:
        chunks.append(current)
    return chunks


async def post_to_discord(channel_id: str, content: str, token: str) -> list[str]:
    """Posts content to Discord, splitting into multiple messages if needed."""
    msg_ids, headers, chunks = [], {"Authorization": f"Bot {token}"}, chunk(content)
    print(f"📤 Posting {len(chunks)} message(s) to channel {channel_id}...", flush=True)
    
    async with httpx.AsyncClient(timeout=30) as client:
        for i, part in enumerate(chunks, 1):
            r = await client.post(f"{DISCORD_API}/channels/{channel_id}/messages", headers=headers, json={"content": part})
            print(f"  Chunk {i}: {r.status_code}", flush=True)
            if r.status_code // 100 != 2:
                raise RuntimeError(f"Discord post failed {r.status_code}: {r.text}")
            msg_ids.append(r.json().get("id", ""))
    return msg_ids


AGENT_PROMPT = """You are a tech event research agent. Collect TECH EVENTS ONLY and compile into an agenda.

**Parameters:** Time frame: {time_frame} | Location: {location}

**Tech events include:** meetups, conferences, hackathons, workshops, AI/ML events, startup events, developer gatherings.
**Exclude:** music, art, sports, general social events.

**Tasks (do each ONCE, then move on):**

1. **Discord** (discord-mcp): 
   - list_channels(guild_id="{guild_id}") → find #events or #announcements → read_messages(channel_id)
   - If Discord fails or no tech events: note "No Discord community events"

2. **X/Twitter**:
   - First, use brave-search-mcp to find 2-3 X/Twitter influencers who post about {location} tech meetups, hackathons, or developer events
   - Then, use x_get_user_tweets (x-api-mcp) to search those users' (using their user ids) recent tweets for events: "from:username {location} meetup OR hackathon OR event"
   - If X fails: note "X unavailable"

3. **Web** (brave-search-mcp): 
   - MAX 3 searches for "{location} tech events {time_frame}", Luma calendars, hackathons
   - Stop searching once you have 3+ events

**Output format:**
**Event Title**
Time & Location: [time and location]
Description: [1 line]
Registration: [link]
Source: [source]

After collecting events (or if none found), output the compiled agenda directly."""


async def main():
    """Main function to run the Discord Agenda Agent."""
    client = AsyncDedalus(timeout=900)  # 15 minutes
    runner = DedalusRunner(client)
    
    print("Discord Agenda Agent\n" + "="*50)
    
    if len(sys.argv) >= 3:
        time_frame, location = sys.argv[1], sys.argv[2]
        print(f"Time: {time_frame} | Location: {location}")
    else:
        time_frame = input("Time frame (e.g., 'next week'): ").strip() or "next week"
        location = input("Location (e.g., 'San Francisco'): ").strip() or "general"
    
    guild_id = os.getenv("DISCORD_GUILD_ID", "")
    
    response = runner.run(
        input=AGENT_PROMPT.format(time_frame=time_frame, location=location, guild_id=guild_id),
        model=["anthropic/claude-opus-4-5"],
        mcp_servers=["windsor/x-api-mcp", "nickyhec/discord-mcp", "tsion/brave-search-mcp"],
        credentials=[x_secrets, discord_secrets],
        stream=True
    )
    
    # Stream and capture the agent's output
    agenda = ""
    async for chunk in response:
        if hasattr(chunk, 'choices'):
            for choice in chunk.choices:
                delta = getattr(choice, 'delta', None)
                if delta and hasattr(delta, 'content') and delta.content:
                    print(delta.content, end='', flush=True)
                    agenda += delta.content
    
    print("\n" + "="*50, flush=True)
    
    # Debugging
    if not agenda.strip():
        print("⚠️ No agenda generated", flush=True)
        return
    
    token = os.getenv("DISCORD_TOKEN", "").strip()
    if not token:
        print("⚠️ No DISCORD_TOKEN, skipping post.", flush=True)
        return
    
    # Format and post to Discord
    formatted = f"📅 **EVENT AGENDA**\n\n{agenda}\n\n---\n*Generated {datetime.now():%Y-%m-%d %H:%M:%S}*"
    channel_id = os.getenv("DISCORD_POST_CHANNEL_ID", "")
    if not channel_id:
        print("⚠️ No DISCORD_POST_CHANNEL_ID, skipping post.", flush=True)
        return
    msg_ids = await post_to_discord(channel_id, formatted, token)
    print(f"✅ Posted to Discord: {msg_ids}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
