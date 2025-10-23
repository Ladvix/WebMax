class InvalidPhoneError(Exception):
    def __init__(self, phone: str):
        super().__init__(f'Неверный формат номера телефона — {phone}')

class NotAuthorizedError(Exception):
    def __init__(self, message: str = 'Требуется авторизация'):
        super().__init__(message)

class ApiError(Exception):
    def __init__(self, message: str):
        super().__init__(message)