import re
from .utils import credentials_utils
from .static import Constants
from .exceptions import InvalidPhoneError

class AuthMixin():
    def __init__(self):
        if not re.match(Constants.PHONE_REGEX, self.phone):
            raise InvalidPhoneError(self.phone)

    async def auth(self):
        temp_token = await self.send_code(phone=self.phone)
        print(f'На номер {self.phone} был отправлен код подтверждения.')
        code = input('Введите полученный вами код: ')

        token = await self.verify_code(code=code, token=temp_token)
        full_name = f'{self.me.firstname} {self.me.lastname}'.strip()
        print(f'Вы авторизованы как {full_name}.')

        self.token = token
        self.credentials = {
            'device_id': self.device_id,
            'token': self.token,
            'phone': self.phone
        }
        credentials_utils.save(self.credentials)