from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import Router, Bot, F
from calendary import calendary as c
from attachements import keyboard as kb
from attachements import buttons as btn
from calendary.common import get_user_locale
from filters.callback import ConfirmCallback
from filters.states import AddRemind
from aiogram.fsm.context import FSMContext
from attachements import message as msg
router = Router()


@router.message(AddRemind.add_description)
@router.callback_query(AddRemind.add_deadline, ConfirmCallback.filter(F.confirm == False))
async def dialog_cal_handler(query: CallbackQuery, state: FSMContext, bot: Bot):
    if await state.get_state() == AddRemind.add_description:
        await state.update_data(remind_description=query.text)
    else:
        await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)

    await bot.send_message(chat_id=query.from_user.id,
        text=msg.INPUT_REMIND_DEADLINE + "Please select a date: ",
        reply_markup=await c.DialogCalendar(
            locale=await get_user_locale(query.from_user)
        ).start_calendar()
    )
    await state.set_state(AddRemind.add_deadline)

@router.callback_query(AddRemind.add_deadline, c.DialogCalendarCallback.filter())
async def process_dialog_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, date = await c.DialogCalendar(
        locale=await get_user_locale(callback_query.from_user)
    ).process_selection(callback_query, callback_data)

    if selected:
        await callback_query.message.answer(
            f'Вы выбрали {date}. Подтвердить введённую дату?',
            reply_markup=kb.get_keyboard(btn.CONFIRMING)
        )
        await state.update_data(choosed_data=date)
        await state.update_data(id_delete_msg=callback_query.message.message_id)
    else:
        print(callback_data)

@router.callback_query(AddRemind.add_deadline, ConfirmCallback.filter(F.confirm == True))
async def date_confirmed(callback_query: CallbackQuery, state: FSMContext):
        await callback_query.message.answer(msg.TRY_INPUT_REMIND_FILE,
                             reply_markup=kb.get_keyboard(btn.CONFIRMING))
        await state.set_state(AddRemind.try_add_file)