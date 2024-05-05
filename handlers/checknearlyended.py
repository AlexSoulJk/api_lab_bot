from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from filters.states import CheckRemind, ChangeRemind
from aiogram import Router, Bot, F, types
from attachements import message as msg
from attachements import keyboard as kb
from attachements import buttons as btn
from attachements import tools as t
from filters.callback import ConfirmCallback, ButLeftRightCallBack, RemindListCallBack, ShowFilesCallBack, \
    BackButtonCallBack, FilesListCallBack, CloseCallBack
from aiogram.types import Message, CallbackQuery, BufferedInputFile, FSInputFile, InputMediaPhoto
from database.db import db
from database.models import User, File, Remind, Category
from sqlalchemy import select, update, null, desc
import datetime

router = Router()

@router.message(Command(commands="check_ended"))
async def check_ended_start(message: Message, state: FSMContext):
    remind_list = db.sql_query(query=select(Remind).where(
        Remind.user_id == message.from_user.id).where(Remind.date_finish != null()))
