from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from attachements import keyboard as kb
from attachements import buttons as btn
from attachements import message as msg
from filters.callback import ConfirmCallback, RemindTypeCallBack
from filters.states import TimePicker, AddRemind, Calendary, ChangeRemind
import datetime
from aiogram.fsm.context import FSMContext
from attachements.clock import ClockCallback
from attachements import clock as c

router = Router()


@router.callback_query(Calendary.start, ConfirmCallback.filter(F.confirm == True))
@router.callback_query(AddRemind.add_deadline_time, ConfirmCallback.filter(F.confirm == False))
async def send_welcome(message: Message, state: FSMContext, bot: Bot):
    # TODO: Подумать над временем, которое здесь используется
    date = (await state.get_data()).get("choosed_data")
    but_, current_hours, current_minutes = c.get_clock(is_today=date == datetime.datetime.now())

    await state.update_data(buttons=but_)
    await state.update_data(choosed_data=date.replace(hour=current_hours,
                                                      minute=current_minutes))

    await bot.send_message(chat_id=message.from_user.id, text='Выберите время',
                           reply_markup=c.get_keyboard_clock_(but_).as_markup())
    await state.set_state(TimePicker.start)


@router.callback_query(TimePicker.start, ClockCallback.filter(F.action == "change"))
@router.callback_query(TimePicker.start, ClockCallback.filter(F.action == 'success'))
async def cb_handler(query: CallbackQuery, callback_data: ClockCallback, state: FSMContext, bot: Bot):
    cur_time = (await state.get_data()).get("choosed_data")
    but_ = (await state.get_data()).get("buttons")
    is_changing = (await state.get_data()).get("is_changing")
    cur_time, flag = c.handle(current_time=cur_time, callback_data=callback_data)

    if flag:

        await bot.edit_message_text(chat_id=query.from_user.id,
                                    text=str(cur_time) + ". " + ("", msg.SHOW_SAMPLE)[is_changing],
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
        c.update(but_, cur_time)
        but = c.get_keyboard_clock_(but_)
        await state.update_data(buttons=but_)
        await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                            message_id=query.message.message_id,
                                            reply_markup=but.as_markup())

    await state.update_data(choosed_data=cur_time)


@router.callback_query(TimePicker.start, ClockCallback.filter(F.action == 'nothing'))
async def nothing(query: CallbackQuery):
    pass


@router.callback_query(AddRemind.end, ConfirmCallback.filter(F.confirm == False))
@router.callback_query(AddRemind.add_type, RemindTypeCallBack.filter(F.type != "common"))
async def interval_start(query: CallbackQuery, state: FSMContext, bot: Bot):
    but_, current_hours, current_minutes = c.get_clock()
    await state.update_data(buttons=but_)
    await state.update_data(interval_time=datetime.datetime(day=10, year=2003, month=7,
                                                            hour=current_hours, minute=current_minutes))
    await bot.send_message(chat_id=query.from_user.id, text='Выберите время',
                           reply_markup=c.get_keyboard_clock_(but_).as_markup())
    await state.set_state(TimePicker.interval_start)


@router.callback_query(TimePicker.interval_start, ClockCallback.filter(F.action == "change"))
@router.callback_query(TimePicker.interval_start, ClockCallback.filter(F.action == 'success'))
async def cb_handler_interval(query: CallbackQuery, callback_data: ClockCallback, state: FSMContext, bot: Bot):
    interval_time = (await state.get_data()).get("interval_time")
    but_ = (await state.get_data()).get("buttons")
    handle_result, flag = c.handle(current_time=interval_time, callback_data=callback_data)

    if flag:
        res_interval = datetime.timedelta(hours=handle_result.hour, minutes=handle_result.minute)
        await bot.edit_message_text(chat_id=query.from_user.id,
                                    text=str(res_interval),
                                    message_id=query.message.message_id, reply_markup=kb.get_keyboard(btn.CONFIRMING))
        await state.update_data(interval_time_=res_interval)
        await state.set_state(AddRemind.end)
    else:
        c.update(but_, handle_result)
        but = c.get_keyboard_clock_(but_)
        await state.update_data(buttons=but_)
        await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                            message_id=query.message.message_id,
                                            reply_markup=but.as_markup())

    await state.update_data(interval_time=handle_result)
