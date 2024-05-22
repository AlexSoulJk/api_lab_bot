from io import BytesIO

from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, BufferedInputFile
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from sqlalchemy import select

from database.db import db
from database.models import File
from filters.callback import FilesListCallBack, FilesListChCallBack
from filters.states import CheckRemind, ChangeRemind
from googledrive.helper import get_credentials
from attachements import keyboard as kb
from attachements import buttons as btn

router = Router()


def get_file(file_id):
    file = db.sql_query(select(File).where(File.id == file_id), is_single=True)
    credentials = get_credentials()
    service = build('drive', 'v3', credentials=credentials)
    request = service.files().get_media(fileId=file.file_url)
    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)

    bf = BufferedInputFile(fh.read(), filename=file.file_name)
    fh.close()
    return bf


@router.callback_query(CheckRemind.check_files_list, FilesListCallBack.filter())
@router.callback_query(ChangeRemind.choose_to_edit, FilesListCallBack.filter(F.file_id > 0))
async def download_file(query: CallbackQuery, callback_data: FilesListCallBack,
                        state: FSMContext, bot: Bot):
    curr_state = (await state.get_state())
    file_id = callback_data.file_id
    await bot.send_document(
        chat_id=query.from_user.id,
        document=get_file(file_id),
    )
    if curr_state == CheckRemind.check_files_list:
        await bot.edit_message_reply_markup(chat_id=query.from_user.id, message_id=query.message.message_id,
                                            reply_markup=kb.get_keyboard(btn.REMIND_MENU_BAR))
        await state.set_state(CheckRemind.check_remind)
    else:
        pass


@router.callback_query(ChangeRemind.choose_to_edit, FilesListCallBack.filter(F.file_id < 0))
async def check_appended_file(query: CallbackQuery, callback_data: FilesListChCallBack,
                              state: FSMContext, bot: Bot):
    curr_file_info = (await state.get_data()).get("add_objects")["files"][callback_data.file_id]
    if curr_file_info[4]:
        await bot.send_document(chat_id=query.from_user.id, document=curr_file_info[3])
    else:
        await bot.send_photo(chat_id=query.from_user.id, photo=curr_file_info[3])
