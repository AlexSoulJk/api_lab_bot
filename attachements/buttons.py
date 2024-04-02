from filters.callback import SkipCallback, ConfirmCallback, RemindTypeCallBack, BackButtonCallBack, \
    ShowFilesCallBack, EditRemindCallBack, EditFilesCallBack, CloseCallBack, EditOptionCallBack, CheckSampleRemind, \
    EditOptionObject, ClockCallback

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
SHOW_FILES = [("Показать вложенные файлы", ShowFilesCallBack(action="show"))]
EDIT_REMIND = [("Изменить.", EditRemindCallBack(action="edit"))]
FINISH_REMIND_URGENTLY = [("Завершить досрочно.", CloseCallBack(action="close_urgently"))]
REMOVE_REMIND = [("Удалить.", CloseCallBack(action="remove_remind"))]
BACK_TO_REMIND_LIST = [("Вернуться к списку напоминаний", BackButtonCallBack(action="back_to_remind_list"))]
# Main remind menu
REMIND_MENU_BAR = SHOW_FILES + EDIT_REMIND + FINISH_REMIND_URGENTLY + BACK_TO_REMIND_LIST + REMOVE_REMIND

CLOSE_REMIND_LIST = [("Закрыть список напоминаний", CloseCallBack(action="close_list"))]
BACK_TO_REMIND = [("Вернуться к напоминанию", BackButtonCallBack(action="back_to_remind"))]

# EDIT REMIND.---------------------------------------------------------------------------------------------
# EDIT REMIND LIST
EDIT_REMIND_LIST = [("Название", EditOptionCallBack(action="name")),
                    ("Описание", EditOptionCallBack(action="description")),
                    ("Дедлайн", EditOptionCallBack(action="date_deadline")),
                    ("Прикреплённые файлы", EditOptionCallBack(action="files")),
                    ("Категорию", EditOptionCallBack(action="categories")),
                    ("Тип", EditOptionCallBack(action="type"))]
# EDIT FILE LIST
ADD_OR_DELETE = [("Удалить", EditFilesCallBack(action="delete")),
                 ("Добавить", EditFilesCallBack(action="add"))]
SUBMIT_DELETE = [("Удаление выбранное", EditOptionObject(is_touched=False, id=-1))]
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

HOLE = [(" ", ClockCallback(action="nothing", typo="hole", data=2003))]