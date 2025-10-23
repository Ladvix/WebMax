from . import payloads
from .entities import Message, User
from .static import Opcode

class ApiMixin():
    def __init__(self):
        pass

    async def ping(self):
        payload_instance = payloads.Ping()
        payload = payload_instance.to_dict()
        
        response = await self.do_api_request(opcode=Opcode.PING, payload=payload)
        return response

    async def init(self, device_id: str, device_version: str, device_name: str):
        payload_instance = payloads.Init(user_agent=self.user_agent, device_id=device_id)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.INIT, payload=payload)
        return response

    async def change_profile_data(self, firstname: str | None = None, lastname: str | None = None, description: str | None = None):
        if not firstname:
            firstname = self.me.firstname
        if not lastname:
            lastname = self.me.lastname
        payload_instance = payloads.ChangeProfileData(firstname=firstname, lastname=lastname, description=description)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.CHANGE_PROFILE_DATA, payload=payload)
        payload = response.get('payload', {})
        profile = payload.get('profile', {})
        contact = profile.get('contact', {})
        self.me = User.from_raw_data(contact)

        return self.me

    async def send_code(self, phone: str):
        payload_instance = payloads.AuthRequest(phone=phone, type='START_AUTH')
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.AUTH_REQUEST, payload=payload)
        payload = response.get('payload', {})
        temp_token = payload.get('token')
        return temp_token

    async def verify_code(self, code: str, token: str):
        payload_instance = payloads.Auth(verify_code=code, token=token)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.AUTH, payload=payload)
        payload = response.get('payload', {})
        tokenAttrs = payload.get('tokenAttrs', {})
        login_data = tokenAttrs.get('LOGIN')
        token = login_data.get('token')
        profile = payload.get('profile')
        contact = profile.get('contact')
        self.me = User.from_raw_data(contact)
        return token

    async def login(self, token: str):
        payload_instance = payloads.Login(token=token)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.LOGIN, payload=payload)
        payload = response.get('payload', {})
        chats = payload.get('chats', [])
        contacts = payload.get('contacts', [])

        for chat in chats:
            id = chat['id']
            self.chats[id] = chat

        for contact in contacts:
            user = User.from_raw_data(contact)
            self.contacts[user.id] = user

        profile = payload.get('profile', {})
        contact = profile.get('contact', {})
        self.me = User.from_raw_data(contact)
        return self.me, self.chats

    async def log_out(self):
        payload_instance = payloads.LogOut()
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.LOG_OUT, payload=payload)
        return response

    async def get_contacts_info(self, contact_ids: list):
        payload_instance = payloads.GetContactsInfo(contact_ids=contact_ids)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.CONTACT_INFO, payload=payload)
        payload = response.get('payload', {})
        contacts = {}
        raw_contacts = payload.get('contacts', [])

        for contact in raw_contacts:
            user = User.from_raw_data(contact)
            contacts[user.id] = user
            self.contacts[user.id] = user
        return contacts

    async def block_user(self, contact_id: int):
        payload_instance = payloads.ContactUpdate(contact_id=contact_id, action='BLOCK')
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.CONTACT_UPDATE, payload=payload)
        return response

    async def unblock_user(self, contact_id: int):
        payload_instance = payloads.ContactUpdate(contact_id=contact_id, action='UNBLOCK')
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.CONTACT_UPDATE, payload=payload)
        return response

    async def add_contact(self, contact_id: int):
        payload_instance = payloads.ContactUpdate(contact_id=contact_id, action='ADD')
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.CONTACT_UPDATE, payload=payload)
        payload = response.get('payload', {})
        user = payload.get('contact')
        if user:
            message = User.from_raw_data(message)
        return message

    async def send_message(self, chat_id: int, cid: int, text: str, link: dict | None = None, elements: list = [], attaches: list = [], notify: bool = True):
        message_instance = payloads.Message(cid=cid, text=text, link=link, elements=elements, attaches=attaches)
        message = message_instance.to_dict()
        payload_instance = payloads.SendMessage(chat_id=chat_id, message=message, notify=notify)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.SEND_MESSAGE, payload=payload)
        payload = response.get('payload', {})
        message = payload.get('message')
        if message:
            message = Message.from_raw_data(message)
        return message

    async def delete_message(self, chat_id: int, message_ids: list, for_me: bool = True):
        payload_instance = payloads.SendMessage(chat_id=chat_id, message_ids=message_ids, for_me=for_me)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.DELETE_MESSAGE, payload=payload)
        return response

    async def edit_message(self, chat_id: int, message_id: int, text: str, elements: list = [], attaches: list = []):
        payload_instance = payloads.SendMessage(chat_id=chat_id, message_id=message_id, text=text, elements=elements, attaches=attaches)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.EDIT_MESSAGE, payload=payload)
        payload = response.get('payload', {})
        message = payload.get('message')
        if message:
            message = Message.from_raw_data(message)
        return message