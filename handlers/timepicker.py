from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from attachements import keyboard as kb
from attachements import buttons as btn
from attachements import message as msg
from filters.callback import ConfirmCallback, RemindTypeCallBack, RemindPeriodicType, BackButtonCallBack, \
    EditOptionCallBack
from filters.states import TimePicker, AddRemind, Calendary, ChangeRemind
import datetime
from aiogram.fsm.context import FSMContext
from attachements.clock import ClockCallback
from attachements import clock as c

router = Router()


@router.callback_query(Calendary.start, ConfirmCallback.filter(F.confirm == True))
@router.callback_query(AddRemind.add_deadline_time, ConfirmCallback.filter(F.confirm == False))
@router.callback_query(AddRemind.add_deadline_end, ConfirmCallback.filter(F.confirm == False))
@router.callback_query(AddRemind.interval_start, ConfirmCallback.filter(F.confirm == False))
async def set_time_start(message: Message, state: FSMContext, bot: Bot):
    curr_state = await state.get_state()
    date = (await state.get_data()).get("choosed_data")
    if curr_state == Calendary.start:
        await bot.edit_message_reply_markup(chat_id=message.from_user.id,
                                            message_id=message.message.message_id,
                                            reply_markup=None)
        # print(message.message.text)
        await bot.edit_message_text(chat_id=message.from_user.id,
                                    message_id=message.message.message_id,
                                    text=message.message.text.replace("Подтвердить введённую дату?", ""))
        await state.update_data(id_msg_calendary=message.message.message_id)

    elif curr_state in [AddRemind.add_deadline_time, AddRemind.add_deadline_end, AddRemind.interval_start]:
        await bot.delete_message(chat_id=message.from_user.id,
                                 message_id=message.message.message_id)
        date.replace(hour=0,
                     minute=0)

    # await bot.delete_message(chat_id=message.from_user.id, message_id=message.message.message_id)

    but_, interval, date = c.get_clock_(is_time=True,
                                        date_start=date,
                                        next_time_to_remind=(await state.get_data()).get("next_remind_time"))

    await state.update_data(buttons=but_)
    await state.update_data(choosed_interval=interval)
    await state.update_data(choosed_data=date)

    await bot.send_message(chat_id=message.from_user.id,
                           text='<b>Выберите время</b>\n'
                                + c.create_current_info_for_time(date, "h"),
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
    cur_change = (await state.get_data()).get("cur_change")
    remind = (await state.get_data()).get("remind_new")

    if cur_change is None:
        cur_change = ""

    is_start_date = (await state.get_data()).get("is_start_date")

    if flag:
        remind_type = (await state.get_data()).get("remind_type")
        await bot.edit_message_text(chat_id=query.from_user.id,
                                    text=f"Выбранное время для {('дедлайна', 'начального')[is_start_date]} напоминания: "
                                         + cur_time.strftime("%H:%M") + ". " +
                                         ("", msg.SHOW_SAMPLE)[is_changing and
                                                               (cur_change != "type"
                                                                or remind_type == "common"
                                                                or not is_start_date)],
                                    message_id=query.message.message_id,
                                    reply_markup=(kb.get_keyboard(btn.CONFIRMING),
                                                  kb.get_keyboard(btn.CHECK_SAMPLE_DEFAULT))[
                                        is_changing and
                                        (cur_change != "type" or
                                         remind_type == "common" or
                                         not is_start_date)])

        if is_changing:
            if cur_change != "type":
                if remind_type == "common":
                    remind[cur_change] = remind["date_deadline"] = cur_time
                else:
                    remind[cur_change] = cur_time
                await state.set_state(ChangeRemind.check_sample)
                await state.update_data(remind_new=remind)
                return

            remind[("date_deadline", "date_last_notificate")[is_start_date]] = cur_time
            await state.update_data(remind_new=remind)

        if is_start_date:
            await state.update_data(date_start=cur_time)
        else:
            await state.update_data(date_deadline=cur_time)

        if remind_type == "common":
            if cur_change == "type":
                remind["date_deadline"] = cur_time
                remind["interval"] = None
                await state.update_data(remind_new=remind)
            await state.set_state((AddRemind.add_deadline_end,
                                   ChangeRemind.check_sample)[is_changing])
        elif remind_type != "common" and is_start_date:
            await state.set_state(AddRemind.interval_start)
        else:
            await state.set_state((AddRemind.add_deadline_end,
                                   ChangeRemind.check_sample)[is_changing])
    else:
        c.update_keyboard(interval, callback_data.typo, but_)
        but = c.get_keyboard_clock(but_, adjust_=(1,))
        await state.update_data(buttons=but_)
        await bot.edit_message_text(chat_id=query.from_user.id,
                                    message_id=query.message.message_id,
                                    text='<b>Выберите время</b>\n' +
                                         c.create_current_info_for_time(cur_time,
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
                                                                    callback_data.typo),
                                reply_markup=but.as_markup(),
                                parse_mode="HTML")


@router.callback_query(AddRemind.interval_start, ConfirmCallback.filter(F.confirm == True))
@router.callback_query(AddRemind.interval_finish, ConfirmCallback.filter(F.confirm == False))
@router.callback_query(ChangeRemind.start, EditOptionCallBack.filter(F.action == "interval"))
async def test_interval_start(query: CallbackQuery, state: FSMContext, bot: Bot):
    curr_state = await state.get_state()

    if curr_state != ChangeRemind.start:
        date_start = (await state.get_data()).get("date_start")
        await bot.delete_message(chat_id=query.from_user.id,
                                 message_id=query.message.message_id)
    else:
        remind = (await state.get_data()).get("remind_new")
        date_start = remind["date_last_notificate"]
        await state.update_data(date_start=date_start)

    if curr_state == AddRemind.interval_start:
        await bot.delete_message(chat_id=query.from_user.id,
                                 message_id=(await state.get_data()).get("id_msg_calendary"))
        await bot.send_message(chat_id=query.from_user.id,
                               text=f'Вы выбрали в качестве начальной даты: {date_start.strftime("%Y-%m-%d %H:%M")}.')

    but_, interval, date_start = c.get_clock_(date_start=date_start)

    await state.update_data(buttons=but_)
    await state.update_data(next_remind_time=date_start)
    await state.update_data(interval_curr=interval)
    await state.update_data(current_index=3)
    await state.update_data(is_start_date=False)

    await bot.send_message(chat_id=query.from_user.id,
                           text='<b>Выберите время</b>\n' + c.create_current_info(date_start,
                                                                                  date_start,
                                                                                  interval,
                                                                                  "h"),
                           reply_markup=c.get_keyboard_clock(but_).as_markup(),
                           parse_mode="HTML")

    await state.set_state(TimePicker.start_)


@router.callback_query(TimePicker.start_, ClockCallback.filter(F.action == "change"))
@router.callback_query(TimePicker.start_, ClockCallback.filter(F.action == 'success'))
async def cb_handler_interval_change(query: CallbackQuery, callback_data: ClockCallback, state: FSMContext, bot: Bot):
    start_time = (await state.get_data()).get("date_start")
    date_curr = (await state.get_data()).get("next_remind_time")
    interval = (await state.get_data()).get("interval_curr")
    but_ = (await state.get_data()).get("buttons")
    is_changing = (await state.get_data()).get("is_changing")
    interval, handle_result, flag = c.handle_interval_change(interval=interval,
                                                             current_time=date_curr,
                                                             callback_data=callback_data)
    cur_change = (await state.get_data()).get("cur_change")

    if cur_change is None:
        cur_change = ""

    if interval.is_zero() and flag:
        return

    if flag:
        date, time = interval.to_string()
        await bot.edit_message_text(chat_id=query.from_user.id,
                                    text=msg.INTERVAL_MSG + date + time +
                                         ("", msg.SHOW_SAMPLE)[is_changing and cur_change != "type"],
                                    message_id=query.message.message_id,
                                    reply_markup=(kb.get_keyboard(btn.CONFIRMING),
                                                  kb.get_keyboard(btn.CHECK_SAMPLE_DEFAULT))[is_changing
                                                                                             and cur_change != "type"])
        if is_changing:
            remind = (await state.get_data()).get("remind_new")
            remind["interval"] = interval
            await state.update_data(remind_new=remind)
        else:
            await state.update_data(interval_time_=interval.to_database())

        await state.set_state((AddRemind.interval_finish,
                               ChangeRemind.check_sample)[is_changing and cur_change != "type"])

    else:
        c.update_keyboard(interval,
                          callback_data.typo,
                          but_)

        but = c.get_keyboard_clock(but_)
        await state.update_data(buttons=but_)
        await bot.edit_message_text(chat_id=query.from_user.id,
                                    message_id=query.message.message_id,
                                    text='<b>Выберите время</b>\n' +
                                         c.create_current_info(start_time,
                                                               handle_result,
                                                               interval,
                                                               callback_data.typo),
                                    reply_markup=but.as_markup(),
                                    parse_mode="HTML")

    await state.update_data(next_remind_time=handle_result)
    await state.update_data(interval_curr=interval)


@router.callback_query(TimePicker.start_, ClockCallback.filter(F.action == "switch"))
async def cb_handler_interval_(query: CallbackQuery, callback_data: ClockCallback, state: FSMContext, bot: Bot):
    start_time = (await state.get_data()).get("date_start")
    date_curr = (await state.get_data()).get("next_remind_time")
    but_ = (await state.get_data()).get("buttons")
    interval = (await state.get_data()).get("interval_curr")

    current_index = c.update_keyboard_switch(interval, callback_data.data, but_)

    but = c.get_keyboard_clock(but_)
    await state.update_data(buttons=but_)
    await state.update_data(current_index=current_index)
    await bot.edit_message_text(chat_id=query.from_user.id,
                                message_id=query.message.message_id,
                                text='<b>Выберите время</b>\n' +
                                     c.create_current_info(start_time,
                                                           date_curr,
                                                           interval,
                                                           callback_data.typo),
                                reply_markup=but.as_markup(),
                                parse_mode="HTML")


@router.callback_query(TimePicker.start_, ClockCallback.filter(F.action == 'nothing'))
@router.callback_query(TimePicker.time_start, ClockCallback.filter(F.action == 'nothing'))
async def nothing(query: CallbackQuery):
    pass
