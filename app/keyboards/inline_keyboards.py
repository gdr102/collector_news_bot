from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def kb_start():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Источники', callback_data='sources')],
        [InlineKeyboardButton(text='Добавить источник', callback_data='add_source')],
        [InlineKeyboardButton(text='Запрещенные категории', callback_data='list_ban_categories')]
    ])


async def kb_sources():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Удалить источник', callback_data='delete_source')],
        [InlineKeyboardButton(text='Меню', callback_data='menu')]
    ])

async def kb_cancel_delete():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Отмена', callback_data='sources')]
    ])

async def kb_add_source():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Да', callback_data='add_source_yes')],
        [InlineKeyboardButton(text='Отмена', callback_data='menu')]
    ])

async def kb_list_categories():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Добавить', callback_data='add_ban_category')],
        [InlineKeyboardButton(text='Меню', callback_data='menu')]
    ])

async def kb_add_ban_categories():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Отмена', callback_data='list_ban_categories')]
    ])

async def kb_add_categories():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Добавить', callback_data='add_ban_categories')],
        [InlineKeyboardButton(text='Меню', callback_data='menu')]
    ])

