from bot import Bot
from config import Config
from database.autofilter import a_filter
from pyrogram import Client, filters
from pyrogram.types import Message

media_filter = filters.document | filters.video | filters.audio


@Client.on_message(filters.chat(Config.CHANNELS) & media_filter)
async def media(bot: Bot, message: Message):
    """Media Handler"""
    for file_type in ("document", "video", "audio"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return

    media.file_type = file_type
    media.caption = message.caption
    media.chat_id = message.chat.id
    media.message_id = message.id
    await a_filter.save_file(media)
