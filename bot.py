import asyncio
import os
import sys
from typing import AsyncGenerator, Optional, Union

from config import Config
from logger import LOGGER
from pyrogram import Client, types


class Bot(Client):
    def __init__(
        self,
        name: str
    ):
        self.is_idling = False
        super().__init__(
            name,
            Config.API_ID, 
            Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins = {'root': 'plugins'}
        )
    

    async def start(self):
        await super().start()
        me = await self.get_me()
        LOGGER("bot").info(f"{me.first_name} started")
        await self.send_message(Config.LOG_CHANNEL, '#START\nBot started')


    async def stop(self, *args):
        await self.send_message(Config.LOG_CHANNEL, f'#STOP\nBot Stopped ')
        await super().stop()

    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        """Iterate through a chat sequentially.
        This convenience method does the same as repeatedly calling :meth:`~pyrogram.Client.get_messages` in a loop, thus saving
        you from the hassle of setting up boilerplate code. It is useful for getting the whole chat messages with a
        single call.
        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).
                
            limit (``int``):
                Identifier of the last message to be returned.
                
            offset (``int``, *optional*):
                Identifier of the first message to be returned.
                Defaults to 0.
        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.
        Example:
            .. code-block:: python
                for message in app.iter_messages("pyrogram", 1, 15000):
                    print(message.text)
        """
        current = offset

        while self.is_idling:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1
            await asyncio.sleep(10)
        
    
    async def stop_and_restart(self):
        os.execl(sys.executable, sys.executable, *sys.argv)
        
        
bot = Bot(Config.BOT_NAME)
