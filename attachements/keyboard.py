from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from filters.callback import RemindListCallBack, ButLeftRightCallBack, FilesListCallBack, EditOptionObject

PER_IN_CHUNK_REMIND_LIST = 2
NEXT_CHUNK = "⯈ "
PAST_CHUNK = " ⯇"


# TODO: Нужно учитывать bad_request от телеграмма в случае,
# если пользователь per_in_chunk <= len

def get_smart_list(items: list[tuple[str, CallbackData]],
                   suport_buttons: list[tuple[str, CallbackData]],
                   number_chunk=1):
    builder = InlineKeyboardBuilder()
    number_chunk_ = number_chunk - 1

    amount_of_chunks = (len(items) + len(items) % PER_IN_CHUNK_REMIND_LIST) // PER_IN_CHUNK_REMIND_LIST
    cur_len = min(PER_IN_CHUNK_REMIND_LIST, len(items) - number_chunk_ * PER_IN_CHUNK_REMIND_LIST)
    cur_chunk = items[number_chunk_ * PER_IN_CHUNK_REMIND_LIST: cur_len + number_chunk_ * PER_IN_CHUNK_REMIND_LIST]

    adjust = (1,) * cur_len
    new_next_chunk = (number_chunk, 0)[number_chunk == amount_of_chunks] + 1
    new_past_chunk = (number_chunk - 1, amount_of_chunks)[number_chunk == 1]

    for item_text, callback_data in cur_chunk:
        builder.button(text=item_text, callback_data=callback_data)

    if PER_IN_CHUNK_REMIND_LIST < len(items):
        builder.button(text=f"{new_past_chunk}/{amount_of_chunks}     " + PAST_CHUNK,
                       callback_data=ButLeftRightCallBack(action="past_chunk", new_chunk=new_past_chunk))

        builder.button(text=NEXT_CHUNK + f"     {new_next_chunk}/{amount_of_chunks}",
                       callback_data=ButLeftRightCallBack(action="next_chunk", new_chunk=new_next_chunk))
        adjust += (2,)

    adjust += (1,)

    for item_text, callback_data in suport_buttons:
        builder.button(text=item_text, callback_data=callback_data)

    adjust += (1,) * len(suport_buttons)
    builder.adjust(*adjust)
    return builder.as_markup()


def get_remind_list_of_btn(items: list[tuple]):
    return [(text, RemindListCallBack(remind_id=item_id)) for text, item_id in items]


def get_files_list_of_btn(items: list[tuple]):
    return [(text, FilesListCallBack(file_id=item_id)) for text, item_id in items]


def get_optional_object_btn(items: list[tuple]):
    return [(text, EditOptionObject(is_touched=False, id=item_id)) for text, item_id in items]


def update_delete_list(items: [(str, EditOptionObject)], id: int):
    res = []
    for item in items:
        if item[1].id == id:
            if not item[1].is_touched:
                res.append(("✔ " + item[0], EditOptionObject(is_touched=True, id=id)))
            else:
                res.append((item[0][2:], EditOptionObject(is_touched=False, id=id)))
        else:
            res.append(item)
    return res


def get_keyboard(buttons: list[tuple[str, CallbackData]], adjust=(1,)):
    builder = InlineKeyboardBuilder()
    for title, callback_data in buttons:
        builder.button(text=title, callback_data=callback_data)
    builder.adjust(*adjust)

    return builder.as_markup()


def get_keyboard_reply(buttons: list[str], adjust=(1,)):
    # buttons: [("text", Admin)]
    builder = ReplyKeyboardBuilder()
    print(buttons)
    for title in buttons:
        builder.button(text=title)
    builder.adjust(*adjust)

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True, selective=True)
