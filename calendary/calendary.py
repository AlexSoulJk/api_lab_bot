import calendar
from datetime import datetime
from typing import Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery

from .schemas import DialogCalendarCallback, DialogCalAct, highlight, superscript
from .common import GenericCalendar
from .config import YEAR_SIZE


class DialogCalendar(GenericCalendar):
    ignore_callback = DialogCalendarCallback(act=DialogCalAct.ignore).pack()  # placeholder for no answer buttons

    async def _get_month_kb(self, year: int, start_date: Optional[datetime] = None):
        """Creates an inline keyboard with months for specified year"""
        today = datetime.now()

        if start_date:
            today = start_date

        now_month, now_year = today.month, today.year
        now_year = today.year

        kb = []
        # first row with year button
        years_row = []
        years_row.append(
            InlineKeyboardButton(
                text=self._labels.cancel_caption,
                callback_data=DialogCalendarCallback(act=DialogCalAct.cancel, year=year, month=1, day=1).pack()
            )
        )
        years_row.append(InlineKeyboardButton(
            text=str(year) if year != today.year else highlight(year),
            callback_data=DialogCalendarCallback(act=DialogCalAct.start, year=year, month=-1, day=-1).pack()
        ))
        years_row.append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
        kb.append(years_row)

        # two rows with 6 months buttons

        def highlight_month():
            month_str = self._labels.months[month - 1]
            if now_month == month and now_year == year:
                return highlight(month_str)
            return month_str

        month_c = 1
        month_b = [[], []]

        if year == now_year:
            while month_c < now_month:
                month_b[(month_c - 1) // 6].append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
                month_c += 1

        for month in range(month_c, 13):
            month_b[(month - 1) // 6].append(InlineKeyboardButton(
                text=highlight_month(),
                callback_data=DialogCalendarCallback(
                    act=DialogCalAct.set_m, year=year, month=month, day=-1
                ).pack()
            ))
        kb.append(month_b[0])
        kb.append(month_b[1])
        return InlineKeyboardMarkup(row_width=6, inline_keyboard=kb)

    async def _get_days_kb(self, year: int, month: int, start_date: Optional[datetime] = None):
        """Creates an inline keyboard with calendar days of month for specified year and month"""

        today = datetime.now()

        if start_date:
            today = start_date

        now_weekday = self._labels.days_of_week[today.weekday()]
        now_month, now_year, now_day = today.month, today.year, today.day

        def highlight_month():
            month_str = self._labels.months[month - 1]
            if now_month == month and now_year == year:
                return highlight(month_str)
            return month_str

        def highlight_weekday():
            if now_month == month and now_year == year and now_weekday == weekday:
                return highlight(weekday)
            return weekday

        def format_day_string():
            date_to_check = datetime(year, month, day)
            if self.min_date and date_to_check < self.min_date:
                return superscript(str(day))
            elif self.max_date and date_to_check > self.max_date:
                return superscript(str(day))
            return str(day)

        def highlight_day():
            day_string = format_day_string()
            if now_month == month and now_year == year and now_day == day:
                return highlight(day_string)
            return day_string

        kb = []
        nav_row = []
        nav_row.append(
            InlineKeyboardButton(
                text=self._labels.cancel_caption,
                callback_data=DialogCalendarCallback(act=DialogCalAct.cancel, year=year, month=1, day=1).pack()
            )
        )
        nav_row.append(InlineKeyboardButton(
            text=str(year) if year != now_year else highlight(year),
            callback_data=DialogCalendarCallback(act=DialogCalAct.start, year=year, month=-1, day=-1).pack()
        ))
        nav_row.append(InlineKeyboardButton(
            text=highlight_month(),
            callback_data=DialogCalendarCallback(act=DialogCalAct.set_y, year=year, month=-1, day=-1).pack()
        ))
        kb.append(nav_row)

        week_days_labels_row = []
        for weekday in self._labels.days_of_week:
            week_days_labels_row.append(InlineKeyboardButton(
                text=highlight_weekday(), callback_data=self.ignore_callback))
        kb.append(week_days_labels_row)

        month_calendar = calendar.monthcalendar(year, month)
        day_c = 1
        if year == now_year and month == now_month:
            j = 0

            while month_calendar[0][j] == 0:
                j += 1

            while day_c < now_day:
                month_calendar[(day_c - 1 + j) // 7][(day_c - 1 + j) % 7] = 0
                day_c += 1

        for week in month_calendar:
            days_row = []
            for day in week:
                if day == 0:
                    days_row.append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
                    continue
                days_row.append(InlineKeyboardButton(
                    text=highlight_day(),
                    callback_data=DialogCalendarCallback(act=DialogCalAct.day, year=year, month=month, day=day).pack()
                ))
            kb.append(days_row)
        return InlineKeyboardMarkup(row_width=7, inline_keyboard=kb)

    async def start_calendar(
            self,
            year: int = datetime.now().year,
            month: int = None,
            year_start: int = None
    ) -> InlineKeyboardMarkup:

        today = datetime.now()

        now_year = (today.year, year_start)[year_start is not None]

        if month:
            return await self._get_days_kb(year, month)

        kb = []
        years_row = []
        g_year = (min(year, now_year), year)[year - now_year >= YEAR_SIZE]

        for value in range(g_year, g_year + YEAR_SIZE):
            years_row.append(InlineKeyboardButton(
                text=str(value) if value != now_year else highlight(value),
                callback_data=DialogCalendarCallback(act=DialogCalAct.set_y, year=value, month=-1, day=-1).pack()
            ))

        kb.append(years_row)

        nav_row = [(InlineKeyboardButton(text=" ",
                                         callback_data=self.ignore_callback),
                    InlineKeyboardButton(text='<<',
                                         callback_data=DialogCalendarCallback(act=DialogCalAct.prev_y, year=year,
                                                                              month=-1, day=-1).pack()
                                         ))[year >= now_year + YEAR_SIZE],
                   InlineKeyboardButton(text=self._labels.cancel_caption,
                                        callback_data=DialogCalendarCallback(act=DialogCalAct.cancel,
                                                                             year=year, month=1, day=1).pack()),
                   InlineKeyboardButton(text='>>',
                                        callback_data=DialogCalendarCallback(act=DialogCalAct.next_y, year=year,
                                                                             month=1, day=1).pack())
                   ]

        kb.append(nav_row)
        return InlineKeyboardMarkup(row_width=YEAR_SIZE, inline_keyboard=kb)

    async def process_selection(self, query: CallbackQuery,
                                data: DialogCalendarCallback,
                                start_date: Optional[datetime] = None) -> tuple:
        return_data = (False, None)
        if data.act == DialogCalAct.ignore:
            await query.answer(cache_time=60)
        if data.act == DialogCalAct.set_y:
            await query.message.edit_reply_markup(reply_markup=await self._get_month_kb(int(data.year), start_date))
        if data.act == DialogCalAct.prev_y:
            new_year = int(data.year) - YEAR_SIZE
            await query.message.edit_reply_markup(reply_markup=await self.start_calendar(year=new_year,
                                                                                         year_start=start_date.year))
        if data.act == DialogCalAct.next_y:
            new_year = int(data.year) + YEAR_SIZE
            await query.message.edit_reply_markup(reply_markup=await self.start_calendar(year=new_year,
                                                                                         year_start=start_date.year))
        if data.act == DialogCalAct.start:
            await query.message.edit_reply_markup(reply_markup=await self.start_calendar(int(data.year),
                                                                                         year_start=start_date.year))
        if data.act == DialogCalAct.set_m:
            await query.message.edit_reply_markup(reply_markup=await self._get_days_kb(int(data.year),
                                                                                       int(data.month),
                                                                                       start_date))
        if data.act == DialogCalAct.day:
            return await self.process_day_select(data, query)

        if data.act == DialogCalAct.cancel:
            await query.message.delete_reply_markup()
            # TODO normal action while clicked cansel
        return return_data
