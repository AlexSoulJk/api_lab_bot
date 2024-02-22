from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def any_types(message: Message):
    await message.answer('You are durila')