from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from attachements import keyboard as kb
from attachements import buttons as btn
from filters.callback import ConfirmCallback
from filters.states import TimePicker, AddRemind
import datetime
from aiogram.fsm.context import FSMContext
from attachements.clock import ClockCallback
from attachements import clock as c

router = Router()


@router.message(Command(commands="timer"))
@router.callback_query(AddRemind.add_deadline, ConfirmCallback.filter(F.confirm == True))
@router.callback_query(AddRemind.add_deadline_time, ConfirmCallback.filter(F.confirm == False))
async def send_welcome(message: Message, state: FSMContext, bot: Bot):
    curr_time = datetime.datetime.now()
    but_ = c.get_clock(current_time=curr_time)
    but = c.get_keyboard_clock_(but_)
    await state.update_data(buttons=but_)
    await state.update_data(curr_time=curr_time)
    await bot.send_message(chat_id=message.from_user.id, text='Выберите время', reply_markup=but.as_markup())
    await state.set_state(TimePicker.start)


@router.callback_query(TimePicker.start, ClockCallback.filter(F.action == "change"))
@router.callback_query(TimePicker.start, ClockCallback.filter(F.action == 'success'))
async def cb_handler(query: CallbackQuery, callback_data: ClockCallback, state: FSMContext, bot: Bot):
    cur_time = (await state.get_data()).get("curr_time")
    but_ = (await state.get_data()).get("buttons")
    handle_result, flag = c.handle(current_time=cur_time, callback_data=callback_data)

    if flag:
        date = (await state.get_data()).get("choosed_data")
        await bot.edit_message_text(chat_id=query.from_user.id,
                                    text=str((date.replace(hour=handle_result.hour,
                                                           minute=handle_result.minute))),
                                    message_id=query.message.message_id, reply_markup=kb.get_keyboard(btn.CONFIRMING))
        await state.update_data(choosed_data=date)
        await state.set_state(AddRemind.add_deadline_time)
    else:
        c.update(but_, handle_result)
        but = c.get_keyboard_clock_(but_)
        await state.update_data(buttons=but_)
        await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                            message_id=query.message.message_id,
                                            reply_markup=but.as_markup())

    await state.update_data(curr_time=handle_result)


@router.callback_query(TimePicker.start, ClockCallback.filter(F.action == 'nothing'))
async def nothing(query: CallbackQuery):
    pass
