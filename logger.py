from logging.handlers import RotatingFileHandler
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            "botlog.txt",
            maxBytes=5000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)



logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger('imdbpy').setLevel(logging.ERROR)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)