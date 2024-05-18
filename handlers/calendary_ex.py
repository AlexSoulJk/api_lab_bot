import datetime

from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import Router, Bot, F
from calendary import calendary as c
from attachements import keyboard as kb
from attachements import buttons as btn
from calendary.common import get_user_locale
from filters.callback import ConfirmCallback, EditOptionCallBack, RemindTypeCallBack, BackButtonCallBack
from filters.states import AddRemind, Calendary, ChangeRemind
from aiogram.fsm.context import FSMContext
from attachements import message as msg

router = Router()


@router.callback_query(AddRemind.add_type, ConfirmCallback.filter(F.confirm == True))
@router.callback_query(Calendary.start, ConfirmCallback.filter(F.confirm == False))
@router.callback_query(ChangeRemind.start, EditOptionCallBack.filter(F.action == "date_deadline"))
@router.callback_query(ChangeRemind.start, EditOptionCallBack.filter(F.action == "date_last_notificate"))
@router.callback_query(AddRemind.interval_finish, ConfirmCallback.filter(F.confirm == True))
@router.callback_query(ChangeRemind.type, ConfirmCallback.filter(F.confirm == True))
async def dialog_cal_handler(query: CallbackQuery, callback_data: CallbackData, state: FSMContext, bot: Bot):
    curr_state = await state.get_state()

    if curr_state != ChangeRemind.start:
        is_start_date = ((await state.get_data()).get("is_start_date"), True)[curr_state == ChangeRemind.type]
        start_date = (datetime.datetime.now(), (await state.get_data()).get("next_remind_time"))[not is_start_date]
        remind_type = (await state.get_data()).get("remind_type")

        if curr_state == ChangeRemind.type:
            new_remind = (await state.get_data()).get("remind_new")
            new_remind["type"] = remind_type

            await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
            await state.update_data(cur_change="type")
            await state.update_data(remind_new=new_remind)
            await state.update_data(is_start_date=is_start_date)
    else:
        is_start_date = callback_data.action == "date_last_notificate"
        new_remind = (await state.get_data()).get("remind_new")
        remind_type = new_remind["type"]
        start_date = (datetime.datetime.now(), new_remind["date_last_notificate"])[not is_start_date]
        await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                            message_id=query.message.message_id,
                                            inline_message_id=query.inline_message_id,
                                            reply_markup=None)
        await state.update_data(cur_change=str(callback_data.action))
        await state.update_data(is_start_date=is_start_date)
        await state.update_data(remind_type=remind_type)
        if not is_start_date:
            await state.update_data(next_remind_time=start_date)

    if curr_state == AddRemind.interval_finish:
        await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
        interval = (await state.get_data()).get("interval_curr").to_string()
        await bot.send_message(chat_id=query.from_user.id, text=msg.FINAL_INTERVAL + interval[0] + interval[1])
    elif curr_state not in [ChangeRemind.start, ChangeRemind.type]:
        await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)

    text_calendary_msg = (msg.INPUT_REMIND_DEADLINE,
                          msg.INPUT_REMIND_START_DATE + (" первое ", " ")[
                              remind_type == "common"]
                          + "напоминание.")[is_start_date]

    id_msg_calendary = await bot.send_message(chat_id=query.from_user.id,
                                              text=text_calendary_msg,
                                              reply_markup=await c.DialogCalendar(
                                                  locale=await get_user_locale(query.from_user)
                                              ).start_calendar(year=start_date.year, year_start=start_date.year)
                                              )

    await state.update_data(id_msg_calendary=id_msg_calendary.message_id)

    await state.set_state(Calendary.start)


@router.callback_query(Calendary.start, c.DialogCalendarCallback.filter())
async def process_dialog_calendar(query: CallbackQuery, callback_data: CallbackData, state: FSMContext, bot: Bot):
    is_start_date = (await state.get_data()).get("is_start_date")
    start_date = (datetime.datetime.now(), (await state.get_data()).get("next_remind_time"))[not is_start_date]
    selected, date = await c.DialogCalendar(
        locale=await get_user_locale(query.from_user)
    ).process_selection(query, callback_data, start_date)

    if selected:
        # await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
        id_to_edit = (await state.get_data()).get("id_msg_calendary")

        calendary_text = f'Вы выбрали в качестве ' \
                         f'{("дедлайна дату", "начальной даты")[(await state.get_data()).get("is_start_date")]}' \
                         f': {date.strftime("%Y-%m-%d")}.' \
                         f'\nПодтвердить введённую дату?'

        await bot.edit_message_text(chat_id=query.from_user.id,
                                    message_id=id_to_edit,
                                    text=calendary_text,
                                    reply_markup=kb.get_keyboard(btn.CONFIRMING)
                                    )
        await state.update_data(choosed_data=date)
