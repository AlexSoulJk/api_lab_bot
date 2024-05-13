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

    def __init__(self, hours=0, minutes=0, days=0, month=0, year=0):

        self.interval_delta = datetime.timedelta(days=days, hours=hours, minutes=minutes)
        self.year = year
        self.month = month

    def to_string(self):

        atrs_date = ["д.", "мес.", "л."]
        atrs_time = ["ч.", "м."]
        res_date = ""
        res_time = ""

        for i, item in enumerate([self.interval_delta.days,
                                  self.month, self.year]):
            if item != 0:
                res_date += f"{item:02}" + atrs_date[i] + " "

        for i, item in enumerate([self.interval_delta.seconds // 3600,
                                  ((self.interval_delta.seconds % 3600) // 60)]):
            if item != 0:
                res_time += f"{item:02}" + atrs_time[i] + " "

        return res_date, res_time

    def is_zero(self):
        return (self.month == self.year == self.interval_delta.days ==
                self.interval_delta.seconds // 3600 == ((self.interval_delta.seconds % 3600) // 60) == 0)

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
        return self.interval_delta.seconds // 3600, (self.interval_delta.seconds % 3600) // 60


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


def get_keyboard_clock(buttons, adjust_=(2,)):
    adjust = (6,) * 2 + adjust_ + (1,)
    builder = InlineKeyboardBuilder()
    for line in buttons:
        for text_, callback_data_ in line:
            builder.button(text=text_, callback_data=callback_data_)

    builder.adjust(*adjust)
    return builder


def get_clock_(is_time=False,
               date_start: Optional[datetime.datetime] = None,
               next_time_to_remind: Optional[datetime.datetime] = None):
    # START POSITION OF CLOCK IS HOURS
    current_key = "h"
    left_right = ([2, 4], [1])[is_time]
    res = [[], [], [], []]

    current_time = (datetime.datetime.now(), next_time_to_remind)[next_time_to_remind is not None]
    is_today = date_start - current_time.replace(hour=0, minute=0, second=0,
                                                 microsecond=0) < datetime.timedelta(days=1)

    if is_today and is_time:
        date_start = date_start.replace(hour=current_time.hour,
                                        minute=current_time.minute)

    current_time_part = 0
    condition_key = CONDITIONS[current_key]
    steps_curr = STEPS_DICT[current_key]

    for i, diff in enumerate(steps_curr):
        if condition_key(current_time_part + diff):
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

    return res, Interval(0, 0), date_start


def handle_interval_change(interval: Interval, current_time: datetime.datetime, callback_data):
    action, typo, data = callback_data.action, callback_data.typo, callback_data.data

    if action == 'success':
        return interval, current_time, True

    if action == 'change':
        return CHANGE_INTERVAL[typo](interval, data), \
            CHANGE[typo](current_time, data), False


def update_keyboard(interval,
                    current_key,
                    buttons):
    condition_key = CONDITIONS[current_key]
    steps_curr = STEPS_DICT[current_key]
    current_part = CHECK_INTERVAL[current_key](interval)
    for i in range(6):
        if condition_key(steps_curr[i] + current_part):
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
                        ):
    prep = msg.INTERVAL_PREP
    date_int, time_int = interval.to_string()
    res1 = "<b>Первое уведомление: </b>" + start_date.strftime("%d-%m-%y %H:%M")
    res2 = "<b>Выбранный интервал: </b>" + \
           date_int + time_int
    res3 = "<b>Следующее уведомление: </b>" + first_notification_date.strftime("%d-%m-%y %H:%M")
    res4 = "<b>Текущий шаг изменения:</b> " + NAME[current_key]

    return res1 + "\n" + res2 + "\n" + res3 + "\n" + res4


def create_current_info_for_time(start_date: datetime.datetime,
                                 current_key):
    res = "<b>Выбранное время: </b>" + start_date.strftime("%d-%m-%y %H:%M") + "\n"
    res += "<b>Текущий шаг изменения:</b> " + NAME[current_key]
    return res


def update_keyboard_switch(interval,
                           index,
                           buttons):
    current_button = btn.CHANGE_INTERVAL[index]
    current_key = current_button[1].typo

    left_btn = btn.CHANGE_INTERVAL[(index - 1) % len(btn.CHANGE_INTERVAL)]
    right_btn = btn.CHANGE_INTERVAL[(index + 1) % len(btn.CHANGE_INTERVAL)]

    update_keyboard(interval, current_key, buttons)

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
