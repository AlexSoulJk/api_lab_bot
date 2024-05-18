from database.models import Remind

# -------------------------------------------------------------------------
# Welcome scenario messages
WELCOME_MSG = "Добро пожаловать пользователь. Как к вам можно обращаться?"
REMEMBER_YOU = "Отлично, я запомнил вас "
WANNA_CHANGE_NAME = ", хотите изменить имя?"
INPUT_NEW_NAME = "Введите новое имя"
CANCEL_CHANGING = "Понял вас, не будем торопиться)"
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
INPUT_REMIND_START_DATE = "Выберите дату, в которую хотели бы получить"
FINAL_INPUT_DATE_START = "Вы выбрали в качестве "
FINAL_INTERVAL = "Вы выбрали интервал повторения: "

MSG_SHOORING_IN_PERIODIC_START_DATE = "Ваше периодическое напоминание начнет приходить с "
TRY_INPUT_REMIND_FILE = "Хотите добавить файл?"
TRY_INPUT_MORE_REMIND_FILE = "Хотите добавить ещё файл?"
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
CHECK_START = " это список добавленных напоминаний:"
CHECK_DAILY_START = " это список напоминаний, которые нужно завершить в течение этого дня."
CHECK_END = "До свидания, "

# -------------------------------------------------------------------------
# Change remind
CHANGE_NAME = "Введите новое название для напоминания."
CHANGE_DESCRIPTION = "Введите новое описание для напоминания."
CHANGE_DEADLINE = "Выберите новую дату."
CHANGE_OPTION = "Выберите действие:"
CHANGE_CATEGORIES_TO_DELETE = "Выберите категории, которые нужно удалить:"
CHANGE_FILE_TO_DELETE = "Выберите файлы, которые нужно удалить:"
CHANGE_TYPE_WARNING = "Вы уверены в изменении типа уведомления? Так вам придётся заново задать " \
                      "всю информацию связанную с временем. Новый тип будет: "
CHANGE_DICT = {"name": CHANGE_NAME,
               "description": CHANGE_DESCRIPTION,
               "date_deadline": CHANGE_DEADLINE}
CHANGE_ADD_FILES = "Отправьте файл, который хотите прикрепить:"
CHANGE_ADD_CATEGORIES = "Напишите категорию, которую хотите добавить для напоминания"
CHANGE_DICT_ADDING_OBJ = {"files": CHANGE_ADD_FILES,
                          "categories": CHANGE_ADD_CATEGORIES}
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
# Close urgently scenario
CLOSE_CONFIRMED = "Ваше напоминание успешно закрыто!\n " \
                  "Чтобы посмотреть список закрытых напоминаний вы можете написать /list_closed"
CLOSE_SHOORING_MSG = "Вы уверены, что хотите завершить напоминание раньше?"
# Interval const

INTERVAL_MSG = "Вы уверены в выбранном интервале в: "
INTERVAL_PREP = ["через ", "и "]

INTERVAL_SUCCSESS = {False: "Напомнить вам ",
                     True: "Напоминать вам "}

MSG_WANNA_CHANGE_DATE_DEADLINE = "Хотите продлить напоминание?"

# TODO: Поработать с оформлением текста в напоминании
def get_remind_text(remind: Remind, categories):
    res = ""
    if categories:
        for tag in categories:
            res += f"#{tag[0].replace(' ', '')} "
    else:
        res = "-"

    return f"<b>Название</b>: {remind.name}\n\n\n" \
           f"<b>Описание</b>: {remind.text}\n\n\n" \
           f"<b>Следующие напоминание</b>: {remind.date_last_notificate.strftime('%Y-%m-%d %H:%M')}" \
           f"\n{('','<b>Окончание напоминаний:</b>' + remind.date_last_notificate.strftime('%Y-%m-%d %H:%M'))[remind.date_last_notificate != remind.date_deadline]}\n" \
           f"<b>Категории</b>: " + res


def get_remind_text_(remind, add_list_categories=None):
    # TODO: Добавить выравнивание по description
    res = ""
    append = ""

    if add_list_categories:
        for tag in add_list_categories:
            append += f"#{tag.replace(' ', '')} "

    categories = remind["categories"]

    if categories:
        for tag, i in categories:
            res += f"#{tag.replace(' ', '')} "
        res += append
    else:
        res = ("-", append)[append != ""]

    interval_info = remind['interval']
    if interval_info is not None:
        tmp = interval_info.to_string()
        interval_info = f'<b>Окончание напоминаний</b>: {remind["date_deadline"].strftime("%Y-%m-%d %H:%M")}\n' \
                        f'<b>Период повторения</b>: {tmp[0] + tmp[1]}\n'
    else:
        interval_info = ""

    return f"<b>Название</b>: {remind['name']}\n\n\n" \
           f"<b>Описание</b>: {remind['description']}\n\n\n" \
           f"<b>Следующие напоминание</b>: {remind['date_last_notificate'].strftime('%Y-%m-%d %H:%M')}\n" \
           f"{interval_info}" \
           f"<b>Category</b>: " + res
