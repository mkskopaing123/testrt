from logger import LOGGER
from bot import bot
from utils.idle import idle
from utils.tools import update_config
import asyncio



async def main():
    await update_config()
    await bot.start()
    LOGGER(__name__).info("Listening for updates from API..")
    await idle()
    await bot.stop()



if __name__ == '__main__':
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except (KeyboardInterrupt, RuntimeError):
        exit()