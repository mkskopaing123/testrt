import math
import re

from cache import Cache
from config import Config
from database.autofilter import a_filter
from logger import LOGGER
from pyrogram import Client, enums, errors, filters, types
from utils.imdb import get_poster
from utils.tools import check_fsub, format_buttons, get_size, parse_link

log = LOGGER(__name__)


@Client.on_message(filters.text & filters.incoming, group=-1)
async def give_filter(bot: Client, message: types.Message):

    if message.text.startswith("/"):
        return  # ignore commands
    
    if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
        return

    if 2 < len(message.text) < 100:
        search = message.text
        files, offset, total_results = await a_filter.get_search_results(search.lower(), offset=0, filter=True)
        if not files:
            return
    else:
        return
    key = f"{message.chat.id}-{message.id}"
    
    Cache.BUTTONS[key] = search
    if Config.IMDB:
        imdb = await get_poster(search, file=(files[0])['file_name'])
    else:
        imdb = {}
    Cache.SEARCH_DATA[key] = files, offset, total_results, imdb
    if message.chat.type == enums.ChatType.PRIVATE:
        btn = await format_buttons(files)
        if offset != "":
            req = message.from_user.id if message.from_user else 0
            btn.append(
                [types.InlineKeyboardButton(text=f"🗓 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
                types.InlineKeyboardButton(text="NEXT ⏩", callback_data=f"next_{req}_{key}_{offset}")]
            )
        else:
            btn.append(
                [types.InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
            )
    else:
        btn = [[types.InlineKeyboardButton('Download', url=f'https://t.me/{bot.me.username}?start=filter{key}')]]
        
    if imdb:
        cap = Config.TEMPLATE.format(
            query=search,
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
        cap = f'Query: {search}\nTotal Results: {total_results}'
    if imdb and imdb.get('poster') and Config.IMDB_POSTER:
        try:
            await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024],
                                    reply_markup=types.InlineKeyboardMarkup(btn),
                                    quote=True)
        except (
            errors.MediaEmpty, 
            errors.PhotoInvalidDimensions, 
            errors.WebpageMediaEmpty
            ):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            await message.reply_photo(
                photo=poster, 
                caption=cap[:1024], 
                reply_markup=types.InlineKeyboardMarkup(btn),
                quote=True)
        except Exception as e:
            log.exception(e)
            await message.reply_text(cap, reply_markup=types.InlineKeyboardMarkup(btn), quote=True)
    else:
        await message.reply_text(
            cap, 
            reply_markup=types.InlineKeyboardMarkup(btn), 
            quote=True,
            disable_web_page_preview=True)
    




@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot: Client, query: types.CallbackQuery):
    _, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("This is not for you", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = Cache.BUTTONS.get(key)
    if not search:
        await query.answer("You are using one of my old messages, please send the request again.", show_alert=True)
        return

    files, n_offset, total = await a_filter.get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return

    btn = await format_buttons(files)

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [types.InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
             types.InlineKeyboardButton(f"📃 Pages {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [types.InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             types.InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                types.InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
                types.InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                types.InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=types.InlineKeyboardMarkup(btn)
        )
    except errors.MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex('^file'))
async def handle_file(bot: Client, query: types.CallbackQuery):
    _, file_id = query.data.split()
    file_info = await a_filter.get_file_details(file_id)
    if not file_info:
        return await query.answer('FileNotFoundError', True)
    query.message.from_user = query.from_user 
    if not await check_fsub(bot, query.message):
        return await query.answer('Please Join My Update Channel and click again')
    await bot.send_cached_media(
        query.from_user.id,
        file_id,
        caption = Config.CUSTOM_FILE_CAPTION.format(
            file_name = file_info['file_name'],
            file_size = get_size(file_info['file_size']),
            caption = file_info['caption']
        ),
        reply_to_message_id=query.message.id

    )
    await query.answer(f'Sending : {file_info["file_name"]}')
