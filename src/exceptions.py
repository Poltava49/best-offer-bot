class MessageHandlerBotError(Exception):
    def __init__(self) -> None:
        super().__init__("Ошибка при получении сообщения пользователя. Return None")
