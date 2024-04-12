import datetime
from typing import Optional

from aiogram.utils.keyboard import InlineKeyboardBuilder
from filters.callback import ClockCallback
import attachements.buttons as btn
import attachements.message as msg


class Interval:
    month: int = 0
    year: int = 0
    interval_delta: datetime.timedelta = datetime.timedelta(days=0, hours=0, minutes=0)

    def __init__(self, hours, minutes):
        self.interval_delta = datetime.timedelta(days=0, hours=hours, minutes=minutes)
        pass

    def to_string(self):
        return f"{self.interval_delta.days:02}д. {self.month:02}мес. {self.year:02} л. ", \
            f"{self.interval_delta.seconds // 3600:02} ч. {((self.interval_delta.seconds % 3600) // 60):02} м. "

    def change_month(self, month_: int):
        self.month += month_
        return self

    def change_year(self, year_: int):
        self.year += year_
        return self

    def change_interval_delta(self, delta: datetime.timedelta):
        self.interval_delta += delta
        return self

    def to_database(self):
        return self.year, self.month, self.interval_delta

    def get_time(self):
        return self.interval_delta.seconds//3600, (self.interval_delta.seconds % 3600) // 60


MINUTE_STEP = 15
HOUR_STEP = 1
MAX_TIME = (23, 59)

STEPS_HOUR = [-5, -2, -1, 1, 2, 5]
STEPS_MINUTE = [-15, -5, -1, 1, 5, 15]

STEPS_DAY = [-7, -3, -1, 1, 3, 7]
STEPS_MONTH = [-6, -3, -1, 1, 3, 6]
STEPS_YEAR = [-5, -2, -1, 1, 2, 5]

STEPS_DICT = {"y": STEPS_YEAR,
              "mo": STEPS_MONTH,
              "d": STEPS_DAY,
              "h": STEPS_HOUR,
              "m": STEPS_MINUTE}

NAME = {"y": "год",
        "mo": "месяц",
        "d": "день",
        "h": "часы",
        "m": "минуты"}

CONDITIONS = {"y": lambda time: 0 <= time < 11,
              "mo": lambda time: 0 <= time < 12,
              "d": lambda time: 0 <= time < 31,
              "h": lambda time: 0 <= time < 24,
              "m": lambda time: 0 <= time <= 59}

CHANGE = {"y": lambda self=datetime.datetime, change_step=int: self.replace(year=self.year + change_step),
          "mo": lambda self=datetime.datetime, change_step=int: self.replace(
              year=self.year + (self.month + change_step) // 12,
              month=(self.month + change_step) % 12),
          "d": lambda self=datetime.datetime, change_step=int: self + datetime.timedelta(days=change_step),
          "h": lambda self=datetime.datetime, change_step=int: self + datetime.timedelta(hours=change_step),
          "m": lambda self=datetime.datetime, change_step=int: self + datetime.timedelta(minutes=change_step)}

CHANGE_INTERVAL = {"y": lambda self=Interval, change_step=int: self.change_year(change_step),
                   "mo": lambda self=Interval, change_step=int: self.change_month(change_step),
                   "d": lambda self=Interval, change_step=int: self.change_interval_delta(
                       datetime.timedelta(days=change_step)),
                   "h": lambda self=Interval, change_step=int: self.change_interval_delta(
                       datetime.timedelta(hours=change_step)),
                   "m": lambda self=Interval, change_step=int: self.change_interval_delta(
                       datetime.timedelta(minutes=change_step))}

CHECK = {"d": lambda self=datetime.datetime: self.day,
         "mo": lambda self=datetime.datetime: self.month,
         "y": lambda self=datetime.datetime.year: self.year,
         "h": lambda self=datetime.datetime: self.hour,
         "m": lambda self=datetime.datetime: self.minute}

CHECK_INTERVAL = {"y": lambda self=Interval: self.year,
                  "mo": lambda self=Interval: self.month,
                  "d": lambda self=Interval: self.interval_delta.days,
                  "h": lambda self=Interval: self.interval_delta.seconds // 3600,
                  "m": lambda self=Interval: (self.interval_delta.seconds % 3600) // 60}


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


def get_keyboard_clock(buttons, adjust_=(2,)):
    adjust = (6,) * 2 + adjust_ + (1,)
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
                if buttons[j][i + 1][0] == " ":
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


def get_clock_(current_key,
               is_time=False, is_today=False, is_periodic_less_day=False,
               finish_date: Optional[datetime.datetime] = None,
               current_date: Optional[datetime.datetime] = None):
    left_right = [2, 4]
    res = [[], [], [], []]

    current_time_part = 0
    current_minute = 0
    current_hours = 0

    if finish_date:
        second_condition = lambda item=int: finish_date >= CHANGE[current_key](current_date, item)
    else:
        second_condition = lambda item=int: True

    if is_today:
        current_time = datetime.datetime.now()
        current_minute = current_time.minute
        current_hours = current_time.hour
        left_right = [1]

    condition_key = CONDITIONS[current_key]
    steps_curr = STEPS_DICT[current_key]

    for i, diff in enumerate(steps_curr):
        if condition_key(current_time_part + diff) and second_condition(diff):
            res[0].append((str(diff), ClockCallback(action='nothing')))
            res[1].append((btn.TEXT_BUTTONS[i], ClockCallback(action='change',
                                                              typo=current_key,
                                                              data=diff)))
        else:
            res[0].append((btn.HOLE[0][0], btn.HOLE[0][1]))
            res[1].append((btn.HOLE[0][0], btn.HOLE[0][1]))

    if not is_time:
        for item in left_right:
            res[2].append(btn.CHANGE_INTERVAL[item])
    else:
        res[2].append(btn.CHANGE_TIME[1])

    res[3].append(('OK', ClockCallback(action="success")))

    return res, (Interval(current_hours, current_minute), Interval(0, 0))[is_periodic_less_day or not is_today]


def handle_interval_change(interval: Interval, current_time: datetime.datetime, callback_data):
    action, typo, data = callback_data.action, callback_data.typo, callback_data.data

    if action == 'success':
        return interval, current_time, True

    if action == 'change':
        return CHANGE_INTERVAL[typo](interval, data), CHANGE[typo](current_time, data), False


def update_keyboard(interval, current_key, buttons,
                    finish_date: Optional[datetime.datetime] = None,
                    current_date: Optional[datetime.datetime] = None):
    condition_key = CONDITIONS[current_key]
    steps_curr = STEPS_DICT[current_key]
    current_part = CHECK_INTERVAL[current_key](interval)

    if finish_date:
        second_condition = lambda item=int: finish_date >= CHANGE[current_key](current_date, item)
    else:
        second_condition = lambda item=int: True

    for i in range(6):
        if condition_key(steps_curr[i] + current_part) and second_condition(steps_curr[i]):
            if buttons[0][i][0] == " " or buttons[1][i][1].typo != current_key:
                buttons[0][i] = (str(steps_curr[i]), ClockCallback(action="nothing"))
                buttons[1][i] = (btn.TEXT_BUTTONS[i], ClockCallback(action="change",
                                                                    typo=current_key,
                                                                    data=steps_curr[i]))
        elif buttons[0][i][0] != " " or buttons[1][i][1].typo != current_key:
            buttons[0][i] = (" ",
                             btn.HOLE[0][1])

            buttons[1][i] = (" ",
                             btn.HOLE[0][1])


def create_current_info(start_date: datetime.datetime,
                        first_notification_date: datetime.datetime,
                        interval: Interval,
                        current_key,
                        is_less_day=False
                        ):
    prep = msg.INTERVAL_PREP[is_less_day]
    date_int, time_int = interval.to_string()
    res1 = "<b>Начальное время: </b>" + start_date.strftime("%d-%m-%y %H:%M")
    res2 = "<b>Выбранный интервал: </b>" + prep[0] + \
           date_int + prep[1] + time_int
    res3 = "<b>Первое уведомление: </b>" + first_notification_date.strftime("%d-%m-%y %H:%M")
    res4 = "<b>Текущий шаг изменения:</b> " + NAME[current_key]

    return res1 + "\n" + res2 + "\n" + res3 + "\n" + res4


def create_current_info_for_time(start_date: datetime.datetime,
                                 interval: Interval,
                                 current_key):
    date_int, time_int = interval.to_string()
    res = "<b>Выбранное время: </b>" + start_date.strftime("%d-%m-%y") + " " + time_int + "\n"
    res += "<b>Текущий шаг изменения:</b> " + NAME[current_key]
    return res


def update_keyboard_switch(interval,
                           index,
                           buttons,
                           finish_date: Optional[datetime.datetime] = None,
                           current_date: Optional[datetime.datetime] = None):
    current_button = btn.CHANGE_INTERVAL[index]
    current_key = current_button[1].typo

    left_btn = btn.CHANGE_INTERVAL[(index - 1) % len(btn.CHANGE_INTERVAL)]
    right_btn = btn.CHANGE_INTERVAL[(index + 1) % len(btn.CHANGE_INTERVAL)]

    update_keyboard(interval, current_key, buttons, finish_date, current_date)

    buttons[2][0] = left_btn
    buttons[2][1] = right_btn
    return current_button[1].data


def update_keyboard_switch_time(interval,
                                index,
                                buttons):

    current_button = btn.CHANGE_TIME[index]
    current_key = current_button[1].typo
    update_keyboard(interval, current_key, buttons)
    buttons[2][0] = btn.CHANGE_TIME[index - 1]
    return current_button[1].data
