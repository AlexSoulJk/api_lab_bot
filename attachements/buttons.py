from filters.callback import SkipCallback, ConfirmCallback, RemindTypeCallBack, BackButtonCallBack, \
    ShowFilesCallBack, EditRemindCallBack, EditFilesCallBack, CloseCallBack, EditOptionCallBack, CheckSampleRemind, \
    EditOptionObject, ClockCallback, RemindPeriodicType

# ---------------------------------------------------------------------------------
# Buttons

# CONFIRM
CONFIRMING = [("Да", ConfirmCallback(confirm=True)),
              ("Нет", ConfirmCallback(confirm=False))]
# SKIP
SKIP = [("Пропустить", SkipCallback(skip=True))]
# Back


BACK = [("Вернуться к", BackButtonCallBack(action="back"))]

# ADD REMIND.----------------------------------------------------------------------------------------------
# TYPE REMIND
TYPE_REMIND = [("Периодическое", RemindTypeCallBack(type="periodic")),
               ("Обычное", RemindTypeCallBack(type="common"))]
# CHECK REMIND.--------------------------------------------------------------------------------------------
# Эмодзи для различных действий
EMOJI_SHOW_FILES = "\U0001F4C1"  # Эмодзи для "Показать вложенные файлы"
EMOJI_EDIT_REMIND = "\U0001F4DD"  # Эмодзи для "Изменить"
EMOJI_FINISH_REMIND_URGENTLY = "\U000026D4"  # Эмодзи для "Завершить досрочно"
EMOJI_REMOVE_REMIND = "\U0001F5D1"  # Эмодзи для "Удалить"
EMOJI_BACK_TO_REMIND_LIST = "\U0001F519"  # Эмодзи для "Вернуться к списку напоминаний"

EMOJI_CLOSE_REMIND_LIST = "\U0001F4AC"  # Эмодзи для "Закрыть список напоминаний"
EMOJI_BACK_TO_REMIND = "\U00002934"  # Эмодзи для "Вернуться к напоминанию"

EMOJI_EDIT_NAME = "\U0001F4D6"  # Эмодзи для "Название"
EMOJI_EDIT_DESCRIPTION = "\U0001F4DD"  # Эмодзи для "Описание"
EMOJI_EDIT_DEADLINE = "\U0001F5D3"  # Эмодзи для "Дедлайн"
EMOJI_EDIT_FILES = "\U0001F4CE"  # Эмодзи для "Прикреплённые файлы"
EMOJI_EDIT_CATEGORIES = "\U0001F4D2"  # Эмодзи для "Категорию"
EMOJI_EDIT_TYPE = "\U0001F4DD"  # Эмодзи для "Тип"

EMOJI_ADD_FILES = "\U00002795"  # Эмодзи для "Добавить"

# Ваши кнопки с добавленными эмодзи
SHOW_FILES = [(f"{EMOJI_SHOW_FILES} Показать вложенные файлы", ShowFilesCallBack(action="show"))]
EDIT_REMIND = [(f"{EMOJI_EDIT_REMIND} Изменить", EditRemindCallBack(action="edit"))]
FINISH_REMIND_URGENTLY = [
    (f"{EMOJI_FINISH_REMIND_URGENTLY} Завершить досрочно", CloseCallBack(action="close_urgently"))]
REMOVE_REMIND = [(f"{EMOJI_REMOVE_REMIND} Удалить", CloseCallBack(action="remove_remind"))]
BACK_TO_REMIND_LIST = [
    (f"{EMOJI_BACK_TO_REMIND_LIST} Вернуться к списку напоминаний", BackButtonCallBack(action="back_to_remind_list"))]
# Main remind menu
REMIND_MENU_BAR = SHOW_FILES + EDIT_REMIND + FINISH_REMIND_URGENTLY + BACK_TO_REMIND_LIST + REMOVE_REMIND

CLOSE_REMIND_LIST = [(f"{EMOJI_CLOSE_REMIND_LIST} Закрыть список напоминаний", CloseCallBack(action="close_list"))]
BACK_TO_REMIND = [(f"{EMOJI_BACK_TO_REMIND} Вернуться к напоминанию", BackButtonCallBack(action="back_to_remind"))]

# EDIT REMIND.---------------------------------------------------------------------------------------------
# EDIT REMIND LIST
EDIT_REMIND_LIST = [
    (f"{EMOJI_EDIT_NAME} Название", EditOptionCallBack(action="name")),
    (f"{EMOJI_EDIT_DESCRIPTION} Описание", EditOptionCallBack(action="description")),
    (f"{EMOJI_EDIT_DEADLINE} Дедлайн", EditOptionCallBack(action="date_deadline")),
    (f"{EMOJI_EDIT_FILES} Прикреплённые файлы", EditOptionCallBack(action="files")),
    (f"{EMOJI_EDIT_CATEGORIES} Категорию", EditOptionCallBack(action="categories")),
    (f"{EMOJI_EDIT_TYPE} Тип", EditOptionCallBack(action="type"))]

# EDIT FILE LIST
ADD_OR_DELETE = [(f"{EMOJI_REMOVE_REMIND}Удалить", EditFilesCallBack(action="delete")),
                 (f"{EMOJI_ADD_FILES} Добавить", EditFilesCallBack(action="add"))]

SUBMIT_DELETE = [("Удалить выбранное", EditOptionObject(is_touched=False, id=-1))]

BACK_TO_EARLIER_REMIND = [("Вернуться к старому виду", BackButtonCallBack(action="back_into_early"))]
BACK_TO_NEW_REMIND = [("Вернуться к новому виду", BackButtonCallBack(action="back_into_new"))]

EDIT_MORE = [("Изменить ещё", EditRemindCallBack(action="edit_more"))]
EDITING_FINISH = [("Завершить изменения", EditRemindCallBack(action="end"))]
EDIT_PART_OF_MENU = EDIT_MORE + EDITING_FINISH

CHECK_SAMPLE = [("Посмотреть", CheckSampleRemind(action="check"))]

CHECK_SAMPLE_DEFAULT = CHECK_SAMPLE + SKIP

# TOOLS DICT
LIST_MOVES = {"reminds": CLOSE_REMIND_LIST,
              "file_btn": BACK_TO_REMIND}

# CLOCK BUTTONS

DECREASE_BUTTONS_MINUTES = [('⯇⯇⯇', ClockCallback(action="change", typo="m", data=-15)),
                            ('⯇⯇', ClockCallback(action="change", typo="m", data=-5)),
                            ('⯇', ClockCallback(action="change", typo="m", data=-1))]

DECREASE_BUTTONS_HOURS = [('⯇⯇⯇', ClockCallback(action="change", typo="h", data=-5)),
                          ('⯇⯇', ClockCallback(action="change", typo="h", data=-2)),
                          ('⯇', ClockCallback(action="change", typo="h", data=-1))]

INCREASE_BUTTONS_MINUTES = [('⯈', ClockCallback(action="change", typo="m", data=1)),
                            ('⯈⯈', ClockCallback(action="change", typo="m", data=5)),
                            ('⯈⯈⯈', ClockCallback(action="change", typo="m", data=15))]

INCREASE_BUTTONS_HOURS = [('⯈', ClockCallback(action="change", typo="h", data=1)),
                          ('⯈⯈', ClockCallback(action="change", typo="h", data=2)),
                          ('⯈⯈⯈', ClockCallback(action="change", typo="h", data=5))]

TEXT_BUTTONS = ['⯇⯇⯇', '⯇⯇', '⯇', '⯈', '⯈⯈', '⯈⯈⯈']

CHANGE_INTERVAL = [("год", ClockCallback(action="switch", typo="y", data=0)),
                   ("месяц", ClockCallback(action="switch", typo="mo", data=1)),
                   ("дни", ClockCallback(action="switch", typo="d", data=2)),
                   ("часы", ClockCallback(action="switch", typo="h", data=3)),
                   ("минуты", ClockCallback(action="switch", typo="m", data=4))]

HOLE = [(" ", ClockCallback(action="nothing", typo="hole", data=2003))]

REMIND_TYPE = [("В определённое время", RemindPeriodicType()),
               ("Каждый постоянный период", RemindPeriodicType(is_at_time=True))]

CHANGE_TIME = [("часы", ClockCallback(action="switch", typo="h", data=0)),
               ("минуты", ClockCallback(action="switch", typo="m", data=1))]