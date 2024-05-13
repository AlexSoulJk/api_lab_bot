from database.models import Remind
from filters.callback import EditOptionObject
from .clock import Interval


def create_tmp(remind: Remind, files, categories) -> dict[str,]:

    if remind.date_deadline != remind.date_last_notificate:
        interval = Interval(days=remind.interval.days, hours=remind.interval.seconds // 3600,
                                 minutes=(remind.interval.seconds % 3600) // 60, year=remind.ones_years,
                                 month=remind.ones_month)
    else:
        interval = None
    return {"name": remind.name,
            "description": remind.text,
            "date_deadline": remind.date_deadline,
            "date_last_notificate": remind.date_last_notificate,
            "interval": interval,
            "files": files,
            "categories": categories
            }


def check_to_delete(items: [(str, EditOptionObject)]) -> [int]:
    res = []
    for text, callback_data in items:
        if callback_data.is_touched:
            res.append(callback_data.id)
    return res


def get_delete_ids(items) -> tuple:
    categories_ids_to_delete = None
    files_ids_to_delete = None
    for item in items:
        if item[0] == "categories":
            categories_ids_to_delete = item[1]
        elif item[0] == "files":
            files_ids_to_delete = item[1]
    return categories_ids_to_delete, files_ids_to_delete


def get_current_items(items, files_ids_to_delete) -> list[tuple]:
    if files_ids_to_delete is None:
        return items

    res = []
    for text, item_id in items:
        if item_id not in files_ids_to_delete:
            res.append((text, item_id))

    return res
