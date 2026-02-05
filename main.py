"""Discord Agenda Agent - Collects tech events and posts to Discord."""
import asyncio
import json
import os
import sys
import httpx
from datetime import datetime
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv
from connection import check_discord_credentials

load_dotenv()

LAST_AGENDA = {"text": ""}
DISCORD_API = "https://discord.com/api/v9"
DISCORD_MAX = 2000


def capture_agenda(agenda_text: str) -> str:
    """Tool stub - actual execution happens on Dedalus servers."""
    return "Agenda captured."


def chunk(text: str, limit: int = DISCORD_MAX) -> list[str]:
    """Splits text into chunks that fit Discord's 2000 char limit."""
    if not text or len(text) <= limit:
        return [text] if text else [""]
    out, cur = [], ""
    for line in text.splitlines(keepends=True):
        while len(line) > limit:
            if cur: out.append(cur); cur = ""
            out.append(line[:limit]); line = line[limit:]
        if len(cur) + len(line) > limit:
            if cur: out.append(cur)
            cur = line
        else:
            cur += line
    if cur: out.append(cur)
    return out


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

**Tasks:**

1. **Discord** (discord-mcp): 
   - Call list_servers() → find "Break In - Dec 2025" server → list_channels(server_id) → read_messages(channel_id, limit=100) 
   - Read from #events, #announcements, #social, #general, #test-whiteballon channels
   - Filter for tech events in time frame. If no tech events found, note "No posted Discord tech community events"

2. **Web/Luma** (brave-search-mcp): 
   - Search for tech Luma calendars and "{location} tech events/hackathons/conferences {time_frame}"

**Output format for EACH event:**
**Event Title**
Time & Location: [time and location]
Description: [1 line]
Registration: [link if available]
Source: [source]

**Rules:** Sort chronologically, remove duplicates.

**Final step:** Call `capture_agenda(agenda_text)` with the compiled agenda. Do NOT call send_message or post to Discord directly."""


def get_agent_prompt():
    """Returns the agent prompt template."""
    return AGENT_PROMPT


async def main():
    """Main function to run the Discord Agenda Agent."""
    client = AsyncDedalus(timeout=900)  # 15 minutes
    runner = DedalusRunner(client)
    check_discord_credentials()
    
    print("Discord Agenda Agent\n" + "="*50)
    
    if len(sys.argv) >= 3:
        time_frame, location = sys.argv[1], sys.argv[2]
        print(f"Time: {time_frame} | Location: {location}")
    else:
        time_frame = input("Time frame (e.g., 'next week'): ").strip() or "next week"
        location = input("Location (e.g., 'San Francisco'): ").strip() or "general"
    
    prompt = get_agent_prompt().format(time_frame=time_frame, location=location)
    
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(line_buffering=True)
    
    print("\nCollecting events...\n", flush=True)
    
    response = runner.run(
        input=prompt,
        model=["anthropic/claude-opus-4-5", "openai/gpt-4-turbo"],
        mcp_servers=["nickyhec/discord-mcp", "tsion/brave-search-mcp"],
        tools=[capture_agenda],
        stream=True
    )
    
    # Stream and capture tool call arguments
    captured = None
    async for chunk in response:
        if not hasattr(chunk, 'choices'): continue
        for choice in chunk.choices:
            # Display content
            if hasattr(choice, 'delta') and choice.delta and hasattr(choice.delta, 'content') and choice.delta.content:
                print(choice.delta.content, end='', flush=True)
            # Capture tool calls from delta or message
            for src in [getattr(choice, 'delta', None), getattr(choice, 'message', None)]:
                if src and hasattr(src, 'tool_calls') and src.tool_calls:
                    for tc in src.tool_calls:
                        if hasattr(tc, 'function') and getattr(tc.function, 'name', '') == 'capture_agenda':
                            try:
                                args = json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments
                                if isinstance(args, dict) and 'agenda_text' in args:
                                    captured = args['agenda_text']
                                    print(f"\n✅ Captured agenda ({len(captured)} chars)", flush=True)
                            except: pass
    
    if captured:
        LAST_AGENDA["text"] = f"📅 **EVENT AGENDA**\n\n{captured}\n\n---\n*Generated {datetime.now():%Y-%m-%d %H:%M:%S}*"
    
    if not LAST_AGENDA["text"]:
        raise RuntimeError("No agenda captured")
    
    token = os.getenv("DISCORD_TOKEN", "").strip()
    if not token:
        print("⚠️ No DISCORD_TOKEN, skipping post.", flush=True)
        return
    
    channel_id = os.getenv("DISCORD_POST_CHANNEL_ID", "1463395829057454194")
    msg_ids = await post_to_discord(channel_id, LAST_AGENDA["text"], token)
    print(f"✅ Posted to Discord: {msg_ids}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
