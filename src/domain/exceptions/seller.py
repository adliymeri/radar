# src/domain/exceptions/seller.py
class SellerAlreadyExistsError(Exception):
    def __init__(self, chat_id: str):
        super().__init__(f"Seller with chat_id {chat_id} already exists.")