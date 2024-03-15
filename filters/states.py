from aiogram.fsm.state import State, StatesGroup

class WellCome(StatesGroup):
    start = State()


class AddRemind(StatesGroup):
    add_name = State()
    add_description = State()
    add_deadline = State()
    try_add_file = State()
    add_file = State()
    try_add_pic = State()
    add_pic = State()
    add_category = State()
    try_add_category = State()
    add_type = State()
    end = State()


class CalendaryS(StatesGroup):
    start = State()


class CheckRemind(StatesGroup):
    start = State()

    generate_list = State()
    check_remind = State()
    check_files_list = State()
    info = State()
    close = State()


class ChangeRemind(StatesGroup):
    start = State()

    change_text = State()
    choose_option = State()
    choose_delete = State()
    change_file = State()
    change_deadline = State()
    change_category = State()
    change_type = State()
    check_sample = State()
    choose_to_edit = State()
