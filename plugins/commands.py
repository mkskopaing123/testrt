import math

from cache import Cache
from config import Config
from logger import LOGGER
from pyrogram import Client, errors, filters, types
from utils.imdb import get_poster
from utils.tools import check_fsub, format_buttons, get_size, parse_link

log = LOGGER(__name__)

START_TEXT = '''Hey {mention} 👋
Iam An Advanced AutoFilter Bot

**@Movie_Zone_KP**
'''

HELP_TEXT = START_TEXT


@Client.on_message(filters.command('start') & filters.incoming)
async def start_handler(bot: Client, msg: types.Message):
    if len(msg.command) > 1:
        _, cmd = msg.command
        if cmd.startswith('filter'):
            if not await check_fsub(bot, msg, cmd):
                return 
            key = cmd.replace('filter', '').strip()
            keyword = Cache.BUTTONS.get(key)
            filter_data = Cache.SEARCH_DATA.get(key)
            if not (keyword and filter_data):
                return await msg.reply('Search Expired\nPlease send movie name again.')
            files, offset, total_results, imdb = filter_data
            sts = await msg.reply('Please Wait...', quote=True)
            btn = await format_buttons(files)
            if offset != "":
                req = msg.from_user.id if msg.from_user else 0
                btn.append(
                    [types.InlineKeyboardButton(text=f"🗓 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
                    types.InlineKeyboardButton(text="NEXT ⏩", callback_data=f"next_{req}_{key}_{offset}")]
                )
            else:
                btn.append(
                    [types.InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
                )
            if imdb:
                cap = Config.TEMPLATE.format(
                    query=keyword,
                    title=imdb['title'],
                    votes=imdb['votes'],
                    aka=imdb["aka"],
                    seasons=imdb["seasons"],
                    box_office=imdb['box_office'],
                    localized_title=imdb['localized_title'],
                    kind=imdb['kind'],
                    imdb_id=imdb["imdb_id"],
                    cast=imdb["cast"],
                    runtime=imdb["runtime"],
                    countries=imdb["countries"],
                    certificates=imdb["certificates"],
                    languages=imdb["languages"],
                    director=imdb["director"],
                    writer=imdb["writer"],
                    producer=imdb["producer"],
                    composer=imdb["composer"],
                    cinematographer=imdb["cinematographer"],
                    music_team=imdb["music_team"],
                    distributors=imdb["distributors"],
                    release_date=imdb['release_date'],
                    year=imdb['year'],
                    genres=imdb['genres'],
                    poster=imdb['poster'],
                    plot=imdb['plot'],
                    rating=imdb['rating'],
                    url=imdb['url'],
                    **locals()
                )
                
            else:
                cap = f"Here is what i found for your query {keyword}"
            if imdb and imdb.get('poster') and Config.IMDB_POSTER:
                try:
                    await msg.reply_photo(photo=imdb.get('poster'), caption=cap[:1024],
                                            reply_markup=types.InlineKeyboardMarkup(btn),
                                            quote=True)
                except (
                    errors.MediaEmpty, 
                    errors.PhotoInvalidDimensions, 
                    errors.WebpageMediaEmpty
                    ):
                    pic = imdb.get('poster')
                    poster = pic.replace('.jpg', "._V1_UX360.jpg")
                    await msg.reply_photo(
                        photo=poster, 
                        caption=cap[:1024], 
                        reply_markup=types.InlineKeyboardMarkup(btn),
                        quote=True)
                except Exception as e:
                    log.exception(e)
                    await msg.reply_text(cap, reply_markup=types.InlineKeyboardMarkup(btn), quote=True)
            else:
                await msg.reply_text(
                    cap, 
                    reply_markup=types.InlineKeyboardMarkup(btn), 
                    quote=True,
                    disable_web_page_preview=True)
            await sts.delete()
            return 


    await msg.reply(
        START_TEXT.format(mention=msg.from_user.mention),
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton('🔖 Join Our Group to Use Me', url='https://t.me/MKS_RequestGroup')
                ]
            ]

        ),
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex('help'), group=-1)

async def help_handler_query(bot: Client, query: types.CallbackQuery):
    await query.answer()
    await query.edit_message_text(
        HELP_TEXT,
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton('◀️ Back', callback_data='back_home')
                ]
            ]

        )
    )

@Client.on_callback_query(filters.regex('back'))

async def home_handler(bot: Client, query: types.CallbackQuery):
    await query.answer()
    await query.edit_message_text(
        START_TEXT.format(mention=query.from_user.mention),
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton('🔖 Join Our Group to Use Me', url='https://t.me/MKS_RequestGroup')
                ]
            ]

        ),
        disable_web_page_preview=True
    )

@Client.on_message(filters.command('help') & filters.incoming)
async def help_handler(bot: Client, msg: types.Message):
    await msg.reply(
        HELP_TEXT
    )



