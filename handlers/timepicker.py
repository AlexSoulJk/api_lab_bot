from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from attachements import keyboard as kb
from attachements import buttons as btn
from attachements import message as msg
from filters.callback import ConfirmCallback, RemindTypeCallBack, RemindPeriodicType
from filters.states import TimePicker, AddRemind, Calendary, ChangeRemind
import datetime
from aiogram.fsm.context import FSMContext
from attachements.clock import ClockCallback
from attachements import clock as c

router = Router()


@router.callback_query(Calendary.start, ConfirmCallback.filter(F.confirm == True))
@router.callback_query(AddRemind.add_deadline_time, ConfirmCallback.filter(F.confirm == False))
async def set_time_start(message: Message, state: FSMContext, bot: Bot):
    date = (await state.get_data()).get("choosed_data")
    but_, interval = c.get_clock_(current_key="h",
                                  is_today=(datetime.datetime.now() - date) < datetime.timedelta(days=1),
                                  is_time=True)
    hours, minutes = interval.get_time()
    date = date.replace(hour=hours,
                        minute=minutes)
    await state.update_data(buttons=but_)
    await state.update_data(choosed_interval=interval)
    await state.update_data(choosed_data=date)

    await bot.send_message(chat_id=message.from_user.id,
                           text=c.create_current_info_for_time(date,
                                                               interval,
                                                               "h"),
                           reply_markup=c.get_keyboard_clock(but_, adjust_=(1,)).as_markup(),
                           parse_mode="HTML")

    await state.set_state(TimePicker.time_start)


@router.callback_query(TimePicker.time_start, ClockCallback.filter(F.action == "change"))
@router.callback_query(TimePicker.time_start, ClockCallback.filter(F.action == 'success'))
async def time_handler(query: CallbackQuery, callback_data: ClockCallback, state: FSMContext, bot: Bot):
    cur_time = (await state.get_data()).get("choosed_data")
    but_ = (await state.get_data()).get("buttons")
    is_changing = (await state.get_data()).get("is_changing")
    interval = (await state.get_data()).get("choosed_interval")
    interval, cur_time, flag = c.handle_interval_change(interval=interval,
                                                        current_time=cur_time,
                                                        callback_data=callback_data)

    if flag:
        await bot.edit_message_text(chat_id=query.from_user.id,
                                    text="Выбранное время: " + cur_time.strftime("%d-%m-%y %H:%M") + ". " +
                                         ("", msg.SHOW_SAMPLE)[is_changing],
                                    message_id=query.message.message_id,
                                    reply_markup=(kb.get_keyboard(btn.CONFIRMING),
                                                  kb.get_keyboard(btn.CHECK_SAMPLE_DEFAULT))[is_changing])
        if is_changing:
            remind = (await state.get_data()).get("remind_new")
            cur_change = (await state.get_data()).get("cur_change")
            remind[cur_change] = cur_time
            await state.update_data(remind_new=remind)

        await state.set_state((AddRemind.add_deadline_time,
                               ChangeRemind.check_sample)[is_changing])
    else:
        c.update_keyboard(interval, callback_data.typo, but_)
        but = c.get_keyboard_clock(but_, adjust_=(1,))
        await state.update_data(buttons=but_)
        await bot.edit_message_text(chat_id=query.from_user.id,
                                    message_id=query.message.message_id,
                                    text='<b>Выберите время</b>\n' +
                                         c.create_current_info_for_time(cur_time,
                                                                        interval,
                                                                        callback_data.typo),
                                    reply_markup=but.as_markup(),
                                    parse_mode="HTML")

    await state.update_data(choosed_data=cur_time)
    await state.update_data(choosed_interval=interval)


@router.callback_query(TimePicker.time_start, ClockCallback.filter(F.action == "switch"))
async def switch_time_handler(query: CallbackQuery, callback_data: ClockCallback, state: FSMContext, bot: Bot):
    cur_time = (await state.get_data()).get("choosed_data")
    but_ = (await state.get_data()).get("buttons")
    interval = (await state.get_data()).get("choosed_interval")

    current_index = c.update_keyboard_switch_time(interval, callback_data.data, but_)

    but = c.get_keyboard_clock(but_, adjust_=(1,))
    await state.update_data(buttons=but_)
    await state.update_data(current_index=current_index)
    await bot.edit_message_text(chat_id=query.from_user.id,
                                message_id=query.message.message_id,
                                text='<b>Выберите время</b>\n' +
                                     c.create_current_info_for_time(cur_time,
                                                                    interval,
                                                                    callback_data.typo),
                                reply_markup=but.as_markup(),
                                parse_mode="HTML")


@router.callback_query(AddRemind.end, ConfirmCallback.filter(F.confirm == False))
@router.callback_query(AddRemind.add_type, RemindTypeCallBack.filter(F.type != "common"))
async def test_interval_starting(query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.send_message(chat_id=query.from_user.id,
                           text="Выберите нужный интервал",
                           reply_markup=kb.get_keyboard(btn.REMIND_TYPE))
    await state.set_state(TimePicker.choose_type)


@router.callback_query(TimePicker.choose_type, RemindPeriodicType.filter())
async def test_interval_start(query: CallbackQuery, callback_data: RemindPeriodicType, state: FSMContext, bot: Bot):
    date_start = datetime.datetime.now()
    date_finish = (await state.get_data()).get("choosed_data")
    test_curr = (date_start.replace(hour=0, minute=0), date_start)[callback_data.is_at_time]

    but_, interval = c.get_clock_("h", is_periodic_less_day=callback_data.is_at_time,
                                  finish_date=date_finish, current_date=test_curr)

    await state.update_data(buttons=but_)
    await state.update_data(test_date=date_start)
    await state.update_data(test_date_curr=test_curr)
    await state.update_data(interval_curr=interval)
    await state.update_data(is_at_time=callback_data.is_at_time)
    await state.update_data(date_finish=date_finish)
    await state.update_data(current_index=3)
    await bot.send_message(chat_id=query.from_user.id,
                           text='<b>Выберите время</b>\n' + c.create_current_info(date_start,
                                                                                  test_curr,
                                                                                  interval,
                                                                                  "h",
                                                                                  is_less_day=callback_data.is_at_time),
                           reply_markup=c.get_keyboard_clock(but_).as_markup(),
                           parse_mode="HTML")

    await state.set_state(TimePicker.start_)


@router.callback_query(TimePicker.start_, ClockCallback.filter(F.action == "change"))
@router.callback_query(TimePicker.start_, ClockCallback.filter(F.action == 'success'))
async def cb_handler_interval_change(query: CallbackQuery, callback_data: ClockCallback, state: FSMContext, bot: Bot):
    start_time = (await state.get_data()).get("test_date")
    date_curr = (await state.get_data()).get("test_date_curr")
    interval = (await state.get_data()).get("interval_curr")
    is_at_time = (await state.get_data()).get("is_at_time")
    but_ = (await state.get_data()).get("buttons")
    date_finish = (await state.get_data()).get("date_finish")

    interval, handle_result, flag = c.handle_interval_change(interval=interval,
                                                             current_time=date_curr,
                                                             callback_data=callback_data)

    if flag:
        prep = msg.INTERVAL_PREP[is_at_time]
        date, time = interval.to_string()
        await bot.edit_message_text(chat_id=query.from_user.id,
                                    text=msg.INTERVAL_SUCCSESS[is_at_time] +
                                         prep[0] + date + prep[1] + time + " период?",
                                    message_id=query.message.message_id, reply_markup=kb.get_keyboard(btn.CONFIRMING))
        await state.update_data(interval_time_=interval.to_database())
        await state.set_state(AddRemind.end)
    else:
        c.update_keyboard(interval, callback_data.typo, but_, date_finish, handle_result)
        but = c.get_keyboard_clock(but_)
        await state.update_data(buttons=but_)
        await bot.edit_message_text(chat_id=query.from_user.id,
                                    message_id=query.message.message_id,
                                    text='<b>Выберите время</b>\n' +
                                         c.create_current_info(start_time,
                                                               handle_result,
                                                               interval,
                                                               callback_data.typo,
                                                               is_less_day=is_at_time),
                                    reply_markup=but.as_markup(),
                                    parse_mode="HTML")

    await state.update_data(test_date_curr=handle_result)
    await state.update_data(interval_curr=interval)


@router.callback_query(TimePicker.start_, ClockCallback.filter(F.action == "switch"))
async def cb_handler_interval_(query: CallbackQuery, callback_data: ClockCallback, state: FSMContext, bot: Bot):
    start_time = (await state.get_data()).get("test_date")
    date_curr = (await state.get_data()).get("test_date_curr")
    but_ = (await state.get_data()).get("buttons")
    is_at_time = (await state.get_data()).get("is_at_time")
    interval = (await state.get_data()).get("interval_curr")
    date_finish = (await state.get_data()).get("date_finish")

    current_index = c.update_keyboard_switch(interval, callback_data.data, but_, finish_date=date_finish,
                                             current_date=date_curr)

    but = c.get_keyboard_clock(but_)
    await state.update_data(buttons=but_)
    await state.update_data(current_index=current_index)
    await bot.edit_message_text(chat_id=query.from_user.id,
                                message_id=query.message.message_id,
                                text='<b>Выберите время</b>\n' +
                                     c.create_current_info(start_time,
                                                           date_curr,
                                                           interval,
                                                           callback_data.typo,
                                                           is_less_day=is_at_time),
                                reply_markup=but.as_markup(),
                                parse_mode="HTML")


@router.callback_query(TimePicker.start_, ClockCallback.filter(F.action == 'nothing'))
@router.callback_query(TimePicker.time_start, ClockCallback.filter(F.action == 'nothing'))
async def nothing(query: CallbackQuery):
    pass
