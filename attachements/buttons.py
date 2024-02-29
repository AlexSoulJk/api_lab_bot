from filters.callback import SkipCallback, ConfirmCallback, RemindTypeCallBack

# ---------------------------------------------------------------------------------
# Buttons

# CONFIRM
CONFIRMING = [("Да", ConfirmCallback(confirm=True)),
              ("Нет", ConfirmCallback(confirm=False))]
# SKIP
SKIP = [("Пропустить", SkipCallback(skip=True)),
        ("Остаться", SkipCallback(skip=False))]
# ADD REMIND.
# TYPE REMIND
TYPE_REMIND = [("Периодическое", RemindTypeCallBack(type="periodic")), ("Обычное", RemindTypeCallBack(type="common"))]
