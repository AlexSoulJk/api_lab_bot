from filters.callback import SkipCallback, ConfirmCallback

# ---------------------------------------------------------------------------------
# Buttons

# CONFIRM
CONFIRMING = [("Да", ConfirmCallback(confirm=True)),
              ("Нет", ConfirmCallback(confirm=False))]
# SKIP
SKIP = [("Пропустить", SkipCallback(skip=True)),
        ("Остаться", SkipCallback(skip=False))]

