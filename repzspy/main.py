import os
import asyncio
import random
from datetime import datetime
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME")
SOURCE_USERNAMES = os.getenv("SOURCE_USERNAMES", "").split(",")
TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID"))

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

media_groups = {}

@client.on(events.NewMessage(chats=SOURCE_USERNAMES))
async def handler(event):
    if not event.photo and not event.media:
        return

    media_group_id = getattr(event.message, "grouped_id", None)

    if media_group_id:
        group = media_groups.setdefault(media_group_id, [])
        group.append(event)
        await asyncio.sleep(2)

        if len(group) > 1:
            await process_gallery(group)
            media_groups.pop(media_group_id, None)
    else:
        await process_single(event)

async def process_gallery(messages):
    caption_msg = next((m for m in messages if m.text), messages[0])
    caption = caption_msg.text or ""
    header = f"🛰 Zdroj: @{caption_msg.chat.username}\n🆔 Msg ID: {caption_msg.id}\n📆 Datum: {caption_msg.date.strftime('%Y-%m-%d %H:%M')}\n\n"

    media = []
    for msg in messages:
        if msg.photo:
            media.append(msg.photo)

    await client.send_file(TARGET_CHAT_ID, files=media, caption=header + caption)

async def process_single(event):
    if not event.photo:
        return
    caption = event.text or ""
    header = f"🛰 Zdroj: @{event.chat.username}\n🆔 Msg ID: {event.id}\n📆 Datum: {event.date.strftime('%Y-%m-%d %H:%M')}\n\n"
    await client.send_file(TARGET_CHAT_ID, file=event.photo, caption=header + caption)

async def main():
    print("👁️‍🗨️ RepzSpy aktivován.")
    await client.start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
