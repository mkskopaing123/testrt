from os import environ
from typing import Union

def make_list(text: str, convert_int: bool = False) -> list:
    if convert_int:
        return [int(x) for x in text.split()]
    return text.split()

def get_config(key: str, default: str = None, is_bool: bool = False) -> Union[str, bool]:
    value = environ.get(key)
    if value is None:
        return default
    if is_bool:
        if value.lower() in ['true', '1', 'on', 'yes']:
            return True
        elif value.lower() in ['false', '0', 'off', 'no']:
            return False
        else:
            raise ValueError
    return value



class Config:

    BOT_TOKEN = get_config('BOT_TOKEN')
    API_ID = int(get_config('API_ID'))
    API_HASH = get_config('API_HASH')

    DATABASE_URI = get_config('DATABASE_URL')
    SESSION_NAME = get_config('DATABASE_NAME', 'FILTER_BOT')
    COLLECTION_NAME = get_config('COLLECTION_NAME', 'FILTERS')

    BOT_NAME = get_config('BOT_NAME', "FILTER_BOT")

    LOG_CHANNEL = int(get_config('LOG_CHANNEL'))
    FORCE_SUB_CHANNEL = int(get_config('FORCE_SUB_CHANNEL'))

    
    
    TEMPLATE = get_config(
        'IMDB_TEMPLATE',
        """<b>🏷 Title</b>: <a href={url}>{title}</a>
🎭 Genres: {genres}
📆 Year: <a href={url}/releaseinfo>{year}</a>
🌟 Rating: <a href={url}/ratings>{rating}</a> / 10 (based on {votes} user ratings.)
☀️ Languages : <code>{languages}</code>
👥 Cast : <code>{cast}</code>
📀 RunTime: {runtime} Minutes
📆 Release Info : {release_date}
🎛 Countries : <code>{countries}</code>""")


    CHANNELS = make_list(get_config('CHANNELS'), True)
    ADMINS = make_list(get_config('ADMINS'), True)
    
    LONG_IMDB_DESCRIPTION = get_config('LONG_IMDB_DESCRIPTION', False, True)
    MAX_LIST_ELM = int(get_config('MAX_LIST_ELM', 5))


    CUSTOM_FILE_CAPTION = get_config(
        'CUSTOM_FILE_CAPTION'
        """{caption}

@Movie_Zone_KP""")

    IMDB = True
    CHANNEL = True
    IMDB_POSTER = True

    USE_CAPTION_FILTER = get_config('USE_CAPTION_FILTER', True, True)


    