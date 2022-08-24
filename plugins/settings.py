from config import Config
from database.config_db import config_db
from pyrogram import Client, errors, filters, types
from utils.tools import CONFIGURABLE, get_bool, get_buttons


@Client.on_message(filters.command('settings') & filters.user(Config.ADMINS))
async def handle_settings(bot: Client, msg: types.Message):
    
    await msg.reply(
        'Configure your bot here',
        reply_markup=types.InlineKeyboardMarkup(get_buttons())
    )


@Client.on_callback_query(filters.regex('^settings'))
async def setup_settings(bot: Client, query: types.CallbackQuery):
    if query.from_user.id not in Config.ADMINS:
        return await query.answer('This is not for you!')
    set_type, key = query.data.split("#")
    if set_type == "settings_info":
        return await query.answer(CONFIGURABLE[key]['help'], show_alert=True)
    
    setattr(Config, key, get_bool(getattr(Config, key)))
    await config_db.update_config(key, getattr(Config, key))
    await query.answer()
    try:
        await query.edit_message_reply_markup(types.InlineKeyboardMarkup(get_buttons()))
    except errors.MessageNotModified:
        pass
    

    