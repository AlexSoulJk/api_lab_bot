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