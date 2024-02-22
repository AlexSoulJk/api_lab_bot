from aiogram.filters import Command
from aiogram import Router
from attachements import message as msg
from aiogram.types import Message

router = Router()


@router.message(Command(commands="info"))
async def start_using(message: Message):
    await message.answer(msg.INFO_MSG)