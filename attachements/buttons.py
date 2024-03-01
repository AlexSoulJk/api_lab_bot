from filters.callback import SkipCallback, ConfirmCallback, RemindTypeCallBack, BackButtonCallBack, \
    ShowFilesCallBack, EditRemindCallBack, EditFilesCallBack

# ---------------------------------------------------------------------------------
# Buttons

# CONFIRM
CONFIRMING = [("Да", ConfirmCallback(confirm=True)),
              ("Нет", ConfirmCallback(confirm=False))]
# SKIP
SKIP = [("Пропустить", SkipCallback(skip=True)),
        ("Остаться", SkipCallback(skip=False))]
# Back


BACK = [("Вернуться к", BackButtonCallBack(action="back"))]

# ADD REMIND.----------------------------------------------------------------------------------------------
# TYPE REMIND
TYPE_REMIND = [("Периодическое", RemindTypeCallBack(type="periodic")),
               ("Обычное", RemindTypeCallBack(type="common"))]
# CHECK REMIND.--------------------------------------------------------------------------------------------
# SHOW FILES
SHOW_FILES = [("Показать вложенные файлы", ShowFilesCallBack(action="show"))]
BACK_TO_REMIND_LIST = [("Вернуться к списку напоминаний", BackButtonCallBack(action="back_to_remind_list"))]
# EDIT REMIND.---------------------------------------------------------------------------------------------
EDIT_REMIND = [("Изменить напоминание", EditRemindCallBack(action="edit"))]
# EDIT REMIND LIST
EDIT_REMIND_LIST = [("Название", EditRemindCallBack(action="name")),
                    ("Описание", EditRemindCallBack(action="description")),
                    ("Дедлайн", EditRemindCallBack(action="date_deadline")),
                    ("Изображение", EditRemindCallBack(action="picture")),
                    ("Прикреплённые файлы", EditRemindCallBack(action="files")),
                    ("Тип", EditRemindCallBack(action="type"))]
# EDIT FILE LIST
ADD_OR_DELITE = [("Удалить", EditFilesCallBack(action="delete")),
                 ("Добавить", EditFilesCallBack(action="add"))]
