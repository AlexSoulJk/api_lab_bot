from database.models import Remind

# -------------------------------------------------------------------------
# Welcome scenario messages
WELCOME_MSG = "Добро пожаловать пользователь. Как к вам можно обращаться?"
REMEMBER_YOU = "Отлично, я запомнил вас "
# -------------------------------------------------------------------------
# Info scenario message
INFO_MSG = "Вы можете использовать следующие команды: \n" \
           "/back - вернуться назад \n" \
           "/add - добавить напоминание \n" \
           "/check_list - просмотреть список текущий напоминаний\n" \
           "/check_done_list - посмотреть спискок сделанных дел\n"
# -------------------------------------------------------------------------
# Adding remind scenario message
INPUT_REMIND_NAME = " введите названия напоминания."
INPUT_REMIND_TEXT = " введите описание, которое связано с этим напоминанием."
INPUT_REMIND_CATEGORY = "Введите категорию напоминания."
TRY_INPUT_REMIND_CATEGORY = "Хотите добавить ещё одну категорию для напоминания?"
INPUT_REMIND_DEADLINE = "Выберите дедлайн для задачи."
TRY_INPUT_REMIND_FILE = "Хотите добавить файл?"
INPUT_REMIND_FILE = "Прикрепите файл, который хотите прикрепить."
TRY_INPUT_REMIND_PICTURE = "Хотите добавить картинку, " \
                           "которая будет отображать задачу?"
INPUT_REMIND_PICTURE = "Прикрепите картинку, которая будет выводиться при напоминании" \
                       "об этой задаче"
INPUT_TYPE_OF_REMIND = "Выберите тип напоминания из предложенных ниже:"
SHORING_MSG = "Вы уверены в выбранном типе напоминания?"
ADDING_FINISH = "Ваше напоминание успешно добавлено!"

# -------------------------------------------------------------------------
# Check remind list
CHECK_START = " это список сделанных вами напоминаний:"
CHECK_END = "До свидания, "

# -------------------------------------------------------------------------
# Change remind
CHANGE_NAME = "Введите новое название для напоминания."
CHANGE_DESCRIPTION = "Введите новое описание для напоминания."
CHANGE_DEADLINE = "Выберите новую дату."
CHANGE_OPTION = "Выберите действие:"
CHANGE_CATEGORIES_TO_DELETE = "Выберите категории, которые нужно удалить:"
CHANGE_FILE_TO_DELETE = "Выберите файлы, которые нужно удалить:"
CHANGE_DICT = {"name": CHANGE_NAME,
               "description": CHANGE_DESCRIPTION,
               "date_deadline": CHANGE_DEADLINE}

CHANGE_DICT_OPTIONAL_OBJ = {"files": CHANGE_FILE_TO_DELETE,
                            "categories": CHANGE_CATEGORIES_TO_DELETE}
#
SHOW_SAMPLE = "Посмотрите как выглядит ваше напоминание перед внесением изменений."

EDIT_FINISH = "Ваше напоминание успешно изменено!"
# -------------------------------------------------------------------------
# Remove remind scenario

REMOVE_SHOORING_MSG = "Вы уверены, что хотите удалить напоминание?"
REMOVE_CONFIRMED = " Ваше напоминание успешно удалено."

# -------------------------------------------------------------------------

# TODO: Поработать с оформлением текста в напоминании
def get_remind_text(remind: Remind, categories):
    res = ""
    if categories:
        for tag in categories:
            res += f"#{tag[0].replace(' ', '')} "
    else:
        res = "-"

    return f"Title: {remind.name}\n\n\n" \
           f"Text: {remind.text}\n\n\n" \
           f"Deadline: {remind.date_deadline.strftime('%Y-%m-%d')}\n" \
           f"Category: " + res


def get_remind_text_(remind, delete_list_categories=None):
    res = ""

    categories = remind["categories"]
    if delete_list_categories:
        categories = []
        for item, i in remind["categories"]:
            if i not in delete_list_categories:
                categories.append((item, i))

    if categories:
        for tag, i in categories:
            res += f"#{tag.replace(' ', '')} "
    else:
        res = "-"

    return f"Title: {remind['name']}\n\n\n" \
           f"Text: {remind['description']}\n\n\n" \
           f"Deadline: {remind['date_deadline'].strftime('%Y-%m-%d')}\n" \
           f"Category: " + res
