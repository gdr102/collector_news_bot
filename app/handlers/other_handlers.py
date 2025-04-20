from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State

from app.bot import bot

from app.utils.disk import YandexDisk
from app.keyboards.inline_keyboards import kb_sources, kb_cancel_delete, kb_add_source, kb_list_categories, kb_add_ban_categories, kb_add_categories

from app.config import DISK_ID, DISK_SECRET, DISK_TOKEN, FILE_SOURCE, FILE_BAN_CATEGORIES, ADMIN_ID

router = Router()

global msg_sources_id, msg_add_title_id, msg_add_link_id, msg_add_categories_id
msg_sources_id = None
msg_add_title_id = None
msg_add_link_id = None
msg_add_categories_id = None

class DeleteSource(StatesGroup):
    source = State()

class AddSource(StatesGroup):
    source_title = State()
    source_link = State()

class AddBanCategories(StatesGroup):
    list_ban_categories = State()

# Подключение к яндекс диску
disk = YandexDisk(DISK_ID, DISK_SECRET, DISK_TOKEN)

@router.callback_query(F.data == 'sources')
async def sources(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    global msg_sources_id

    user_id = callback.from_user.id

    if user_id == ADMIN_ID:
        msg_load = await callback.message.answer(text='🔃 Загружаю информацию, пожалуйста, подождите...')
        await callback.message.delete() if msg_load else None

        await disk.init_client()  # Инициализируем клиента
        list_sources = await disk.get_sources(FILE_SOURCE)

        message_text = '🗒️ Источники:\n\n'
        for i, source in enumerate(list_sources):
            message_text += f'{i+1}. <a href="{source[1]}">{source[0]}</a>\n'
        message_text += '\n🗑️ Для удаления источника нажмите кнопку ниже и напишите порядковый номер источника 👇'

        msg_sources = await callback.message.answer(text=message_text, reply_markup=await kb_sources(), parse_mode=ParseMode.HTML)
        msg_sources_id = msg_sources.message_id
        await msg_load.delete() if msg_sources else None

@router.callback_query(StateFilter(None), F.data == 'delete_source')
async def delete_source_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=await kb_cancel_delete())

    await state.set_state(DeleteSource.source)

@router.message(DeleteSource.source)
async def delete_source(message: Message, state: FSMContext):
    global msg_sources_id
    chat_id = message.chat.id
    number = int(message.text)

    await message.delete()
    await bot.delete_message(chat_id=chat_id, message_id=msg_sources_id)

    msg_delete = await message.answer(text=f'🔃 Отправляю запрос на удаление источника с порядковым номером — {number} ...')
    await disk.init_client()  # Инициализируем клиента
    res = await disk.delete_source(FILE_SOURCE, number)

    if res:
        msg_load = await message.answer(text='🔃 Загружаю информацию, пожалуйста, подождите...')
        await msg_delete.delete() if msg_load else None

        list_sources = await disk.get_sources(FILE_SOURCE)

        message_text = '🗒️ Источники:\n\n'
        for i, source in enumerate(list_sources):
            message_text += f'{i+1}. <a href="{source[1]}">{source[0]}</a>\n'
        message_text += '\n🗑️ Для удаления источника нажмите кнопку ниже и напишите порядковый номер источника 👇'

        msg_sources = await message.answer(text=message_text, reply_markup=await kb_sources(), parse_mode=ParseMode.HTML)
        msg_sources_id = msg_sources.message_id
        await msg_load.delete() if msg_sources else None


    await state.clear()

@router.callback_query(F.data == 'add_source')
async def add_source(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    global msg_add_title_id
    user_id = callback.from_user.id

    if user_id == ADMIN_ID:
        await callback.message.delete()

        msg_add_title = await callback.message.answer(text='🔤 Отправьте название источника:')
        msg_add_title_id = msg_add_title.message_id
        await state.set_state(AddSource.source_title)

@router.message(AddSource.source_title)
async def add_source_title(message: Message, state: FSMContext):
    global msg_add_title_id, msg_add_link_id

    chat_id = message.chat.id
    await state.update_data(title=message.text)

    await message.delete()
    await bot.delete_message(chat_id=chat_id, message_id=msg_add_title_id)

    msg_add_link = await message.answer(text='🔤 Отправьте ссылку на источник (RSS):')
    msg_add_link_id = msg_add_link.message_id

    await state.set_state(AddSource.source_link)

@router.message(AddSource.source_link)
async def add_source_link(message: Message, state: FSMContext):
    global msg_add_link_id

    chat_id = message.chat.id
    await state.update_data(link=message.text)

    data = await state.get_data()

    await message.delete()
    await bot.delete_message(chat_id=chat_id, message_id=msg_add_link_id)

    await message.answer(
        text=f'🔤 Вы действительно хотите добавить источник?\n\n{data["title"]} - {data["link"]}', 
        reply_markup=await kb_add_source())
    

@router.callback_query(F.data == 'add_source_yes')
async def add_source_yes(callback: CallbackQuery, state: FSMContext):
    global msg_sources_id

    user_id = callback.from_user.id
    data = await state.get_data()

    if user_id == ADMIN_ID:
        await callback.message.delete()

        msg_add_source = await callback.message.answer(text='🔃 Добавляю новый источник, пожалуйста, подождите...')

        await disk.init_client()  # Инициализируем клиента
        res = await disk.add_source(FILE_SOURCE, data['title'], data['link'])

        if res:
            msg_load = await callback.message.answer(text='🔃 Загружаю информацию, пожалуйста, подождите...')
            await msg_add_source.delete() if msg_load else None

            list_sources = await disk.get_sources(FILE_SOURCE)

            message_text = '🗒️ Источники:\n\n'
            for i, source in enumerate(list_sources):
                message_text += f'{i+1}. <a href="{source[1]}">{source[0]}</a>\n'
            message_text += '\n🗑️ Для удаления источника нажмите кнопку ниже и напишите порядковый номер источника 👇'

            msg_sources = await callback.message.answer(text=message_text, reply_markup=await kb_sources(), parse_mode=ParseMode.HTML)
            msg_sources_id = msg_sources.message_id
            await msg_load.delete() if msg_sources else None


    await state.clear()


@router.callback_query(F.data == 'list_ban_categories')
async def list_ban_categories(callback: CallbackQuery):
    user_id = callback.from_user.id

    if user_id == ADMIN_ID:
        msg_load = await callback.message.answer(text='🔃 Загружаю информацию, пожалуйста, подождите...')
        await callback.message.delete() if msg_load else None

        await disk.init_client()  # Инициализируем клиента
        categories = await disk.get_ban_categories(FILE_BAN_CATEGORIES)

        categories_str = ', '.join([f'{category}' for category in categories]) if categories else ''

        msg_list_categories = await callback.message.answer(
            text=f'Список запрещенных категорий:\n\n{categories_str}', 
            reply_markup=await kb_list_categories())
        
        await msg_load.delete() if msg_list_categories else None

@router.callback_query(F.data == 'add_ban_category')
async def add_ban_category(callback: CallbackQuery, state: FSMContext):
    global msg_add_categories_id
    user_id = callback.from_user.id

    if user_id == ADMIN_ID:
        text_msg = f'{callback.message.text}\n\n🔤 Для добавления новых запрещенных категорий отправьте их одним сообщением перечисляя через запятую: 👇'

        msg_add_categories = await callback.message.edit_text(
            text=text_msg,
            reply_markup=await kb_add_ban_categories())
        msg_add_categories_id = msg_add_categories.message_id
        await state.set_state(AddBanCategories.list_ban_categories)

@router.message(AddBanCategories.list_ban_categories)
async def list_categories(message: Message, state: FSMContext):
    global msg_add_categories_id

    chat_id = message.chat.id
    await state.update_data(categories=message.text)

    await message.delete()
    await bot.delete_message(chat_id=chat_id, message_id=msg_add_categories_id)

    await message.answer(text=f'🔤 Добавить?\n\n{message.text}', reply_markup=await kb_add_categories())

@router.callback_query(F.data == 'add_ban_categories')
async def add_ban_categories(callback: CallbackQuery, state: FSMContext):
    global msg_add_categories_id
    user_id = callback.from_user.id

    data = await state.get_data()

    if user_id == ADMIN_ID:
        await callback.message.delete()
        msg_categoreis = await callback.message.answer(text='🔃 Обновляю список запрещенных категорий, пожалуйста, подождите...')

        categories_list = data['categories'].split(', ')

        await disk.init_client()  # Инициализируем клиента
        res = await disk.add_new_categories(FILE_BAN_CATEGORIES, categories_list)

        if res:
            msg_load = await callback.message.answer(text='🔃 Загружаю информацию, пожалуйста, подождите...')
            await msg_categoreis.delete() if msg_load else None

            await disk.init_client()  # Инициализируем клиента
            categories = await disk.get_ban_categories(FILE_BAN_CATEGORIES)

            categories_str = ', '.join([f'{category}' for category in categories]) if categories else ''

            msg_list_categories = await callback.message.answer(
                text=f'Список запрещенных категорий:\n\n{categories_str}', 
                reply_markup=await kb_list_categories())
            
            await msg_load.delete() if msg_list_categories else None


    await state.clear()
    