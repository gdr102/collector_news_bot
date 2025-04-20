from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.keyboards.inline_keyboards import kb_start

from app.config import ADMIN_ID

router = Router()

@router.message(CommandStart())
async def main_menu(message: Message):
    user_id = message.from_user.id

    if user_id == ADMIN_ID:
        await message.answer(text='🖥️ Панель управления Collector News:', reply_markup=await kb_start())

@router.callback_query(F.data == 'menu')
async def main_menu_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id

    if user_id == ADMIN_ID:
        await callback.message.delete()
        await callback.message.answer(text='🖥️ Панель управления Collector News:', reply_markup=await kb_start())

