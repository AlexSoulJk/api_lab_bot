from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import Router, Bot, F
from calendary import calendary as c
from attachements import keyboard as kb
from attachements import buttons as btn
from calendary.common import get_user_locale
from filters.callback import ConfirmCallback, EditOptionCallBack
from filters.states import AddRemind, Calendary, ChangeRemind
from aiogram.fsm.context import FSMContext
from attachements import message as msg

router = Router()


@router.message(AddRemind.add_description)
@router.callback_query(Calendary.start, ConfirmCallback.filter(F.confirm == False))
@router.callback_query(ChangeRemind.start, EditOptionCallBack.filter(F.action == "date_deadline"))
async def dialog_cal_handler(query: CallbackQuery, state: FSMContext, bot: Bot):
    curr_state = await state.get_state()
    if curr_state == AddRemind.add_description:
        await state.update_data(remind_description=query.text)
    elif curr_state == ChangeRemind.start:
        await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                            message_id=query.message.message_id,
                                            inline_message_id=query.inline_message_id,
                                            reply_markup=None)
        await state.update_data(cur_change="date_deadline")
    else:
        await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)

    await bot.send_message(chat_id=query.from_user.id,
                           text=msg.INPUT_REMIND_DEADLINE + "Please select a date: ",
                           reply_markup=await c.DialogCalendar(
                               locale=await get_user_locale(query.from_user)
                           ).start_calendar()
                           )
    await state.set_state(Calendary.start)


@router.callback_query(Calendary.start, c.DialogCalendarCallback.filter())
async def process_dialog_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, date = await c.DialogCalendar(
        locale=await get_user_locale(callback_query.from_user)
    ).process_selection(callback_query, callback_data)

    if selected:

        await callback_query.message.answer(
            f'Вы выбрали {date.strftime("%Y-%m-%d")}. Подтвердить введённую дату?',
            reply_markup=kb.get_keyboard(btn.CONFIRMING)
        )
        await state.update_data(choosed_data=date)
        await state.update_data(id_delete_msg=callback_query.message.message_id)
    else:
        print(callback_data)
