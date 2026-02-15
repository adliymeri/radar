from src.domain.exceptions.base import EntityAlreadyExistsError


class BuyerAlreadyExistsError(EntityAlreadyExistsError):
    def __init__(self, chat_id: str):
        super().__init__(f"Buyer with Chat ID {chat_id} already exists.")