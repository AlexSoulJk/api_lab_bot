import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from filters.callback import ClockCallback
import attachements.buttons as btn

MINUTE_STEP = 15
HOUR_STEP = 1
MAX_TIME = (23, 59)

STEPS_HOUR = [-5, -2, -1, 1, 2, 5]
STEPS_MINUTE = [-15, -5, -1, 1, 5, 15]
CONDITIONS = {"h": lambda time: 0 <= time < 24,
              "m": lambda time: 0 <= time <= 59}


def get_clock(is_today=False):
    res = [[], [], [], [], []]

    current_minute = 0
    current_hours = 0

    if is_today:
        current_time = datetime.datetime.now()
        current_minute = current_time.minute
        current_hours = current_time.hour

    condition_m = CONDITIONS["m"]
    condition_h = CONDITIONS["h"]
    for diff in STEPS_HOUR:
        if condition_h(current_hours + diff):
            res[0].append((str(diff), ClockCallback(action='nothing')))
        else:
            res[0].append((btn.HOLE[0][0], btn.HOLE[0][1]))

        if diff == -1:
            res[0].append(("⯆\nh", ClockCallback(action='nothing')))

    current_minute_buttons = btn.DECREASE_BUTTONS_MINUTES + btn.INCREASE_BUTTONS_MINUTES

    current_hour_buttons = btn.DECREASE_BUTTONS_HOURS + btn.INCREASE_BUTTONS_HOURS

    for index, (text_, callback_data_) in enumerate(current_hour_buttons):
        if condition_h(current_hours + STEPS_HOUR[index]):
            res[1].append((text_, callback_data_))
        else:
            res[1].append((btn.HOLE[0][0], btn.HOLE[0][1]))

        if STEPS_HOUR[index] == -1:
            res[1].append((str(current_hours), ClockCallback(action='current', typo="h")))

    for index, (text_, callback_data_) in enumerate(current_minute_buttons):
        if condition_m(current_minute + STEPS_MINUTE[index]):
            res[2].append((text_, callback_data_))
        else:
            res[2].append((btn.HOLE[0][0], btn.HOLE[0][1]))
        if STEPS_MINUTE[index] == -1:
            res[2].append((str(current_minute),
                           ClockCallback(action='current', typo="m")))

    for diff in STEPS_MINUTE:
        if condition_m(current_minute + diff):
            res[3].append((str(diff), ClockCallback(action='nothing')))
        else:
            res[3].append((btn.HOLE[0][0], btn.HOLE[0][1]))
        if diff == -1:
            res[3].append(("m\n⯅", ClockCallback(action='nothing')))

    res[4].append(('OK', ClockCallback(action="success")))
    return res, current_hours, current_minute


def get_keyboard_clock_(buttons):
    adjust = (7,) * 4 + (1,)
    builder = InlineKeyboardBuilder()
    for line in buttons:
        for text_, callback_data_ in line:
            builder.button(text=text_, callback_data=callback_data_)

    builder.adjust(*adjust)
    return builder


def handle(current_time, callback_data):
    action, typo, data = callback_data.action, callback_data.typo, callback_data.data
    minute_step_date_time = datetime.timedelta(minutes=1)
    hour_step_date_time = datetime.timedelta(hours=1)

    if action == 'success':
        return current_time, True

    if action == 'change':
        if typo == 'h':
            current_time += data * hour_step_date_time
        elif typo == 'm':
            current_time += data * minute_step_date_time
    return current_time, False


def update(buttons, current_time):

    condition_m = CONDITIONS["m"]
    condition_h = CONDITIONS["h"]

    hour = current_time.hour
    minutes = current_time.minute
    buttons[1][3] = (str(hour), ClockCallback(action='nothing'))
    buttons[2][3] = (str(minutes), ClockCallback(action='nothing'))
    current_minute_buttons = btn.DECREASE_BUTTONS_MINUTES + btn.INCREASE_BUTTONS_MINUTES

    current_hour_buttons = btn.DECREASE_BUTTONS_HOURS + btn.INCREASE_BUTTONS_HOURS

    for i in range(3):
        for j in range(2):
            if condition_h(hour + STEPS_HOUR[i]):
                if buttons[j][i][0] == " ":
                    buttons[j][i] = ((str(STEPS_HOUR[i]), ClockCallback(action='nothing')),
                                     current_hour_buttons[i])[j % 2]

            elif buttons[j][i][0] != " ":
                buttons[j][i] = (" ", btn.HOLE[0][1])

        for j in range(2, 4):
            if condition_m(minutes + STEPS_MINUTE[i]):
                if buttons[j][i][0] == " ":
                    buttons[j][i] = (current_minute_buttons[i],
                                        (str(STEPS_MINUTE[i]), ClockCallback(action='nothing'))
                                        )[j % 2]

            elif buttons[j][i][0] != " ":
                buttons[j][i] = (" ", btn.HOLE[0][1])

    for i in range(3, len(STEPS_HOUR)):
        for j in range(2):
            if condition_h(hour + STEPS_HOUR[i]):
                if buttons[j][i+1][0] == " ":
                    buttons[j][i + 1] = ((str(STEPS_HOUR[i]), ClockCallback(action='nothing')),
                                            current_hour_buttons[i])[j % 2]
            elif buttons[j][i + 1][0] != " ":
                buttons[j][i + 1] = (" ", btn.HOLE[0][1])

        for j in range(2, 4):
            if condition_m(minutes + STEPS_MINUTE[i]):
                if buttons[j][i + 1][0] == " ":
                    buttons[j][i + 1] = (
                        current_minute_buttons[i],
                        (str(STEPS_MINUTE[i]), ClockCallback(action='nothing'))
                                        )[j % 2]
            elif buttons[j][i + 1][0] != " ":
                buttons[j][i + 1] = (" ", btn.HOLE[0][1])