from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

router = Router()


@router.message()
async def any_types(message: Message):
    await message.answer('You are durila')
