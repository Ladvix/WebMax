from typing import Tuple
from . import payloads
from .static import ContactActions, Opcode
from .entities import Chat, Element, FileAttach, Message, PhotoAttach, User, VideoAttach

class ApiMixin():
    def __init__(self):
        pass

    def get_chat_id(self, user_id):
        return self.me.id^user_id

    async def ping(self) -> dict:
        payload_instance = payloads.Ping()
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.PING, payload=payload)
        return response

    async def init(self, device_id: str) -> dict:
        payload_instance = payloads.Init(user_agent=self.user_agent, device_id=device_id)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.INIT, payload=payload)
        return response

    async def change_profile_data(self, firstname: str | None = None, lastname: str | None = None, description: str | None = None) -> User:
        if not firstname:
            firstname = self.me.firstname
        if not lastname:
            lastname = self.me.lastname
        payload_instance = payloads.ChangeProfileData(firstname=firstname, lastname=lastname, description=description)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.CHANGE_PROFILE_DATA, payload=payload)
        payload = response.get('payload', {})
        profile = payload.get('profile', {})
        raw_contact = profile.get('contact', {})
        self.me = User.from_raw_data(raw_contact)
        self.contacts[self.me.id] = self.me
        return self.me

    async def send_code(self, phone: str) -> str:
        payload_instance = payloads.AuthRequest(phone=phone, type='START_AUTH')
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.AUTH_REQUEST, payload=payload)
        payload = response.get('payload', {})
        temp_token = payload.get('token')
        return temp_token

    async def verify_code(self, code: str, token: str) -> str:
        payload_instance = payloads.Auth(verify_code=code, token=token)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.AUTH, payload=payload)
        payload = response.get('payload', {})
        tokenAttrs = payload.get('tokenAttrs', {})
        login_data = tokenAttrs.get('LOGIN')
        token = login_data.get('token')
        profile = payload.get('profile')
        raw_contact = profile.get('contact')
        self.me = User.from_raw_data(raw_contact)
        return token

    async def login(self, token: str) -> Tuple[User, list[Chat]]:
        payload_instance = payloads.Login(token=token)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.LOGIN, payload=payload)
        payload = response.get('payload', {})
        chats = payload.get('chats', [])
        contacts = payload.get('contacts', [])

        for raw_chat in chats:
            chat = Chat.from_raw_data(raw_data=raw_chat, client=self)
            self.chats[chat.id] = chat

        for raw_contact in contacts:
            user = User.from_raw_data(raw_contact)
            self.contacts[user.id] = user

        profile = payload.get('profile', {})
        raw_contact = profile.get('contact', {})
        self.me = User.from_raw_data(raw_contact)
        self.contacts[self.me.id] = self.me
        return self.me, self.chats

    async def log_out(self) -> dict:
        payload_instance = payloads.LogOut()
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.LOG_OUT, payload=payload)
        return response

    async def get_contacts_info(self, contact_ids: list[int]) -> dict:
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

    async def update_contact(self, contact_id: int, action: ContactActions) -> User:
        payload_instance = payloads.ContactUpdate(contact_id=contact_id, action=action)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.CONTACT_UPDATE, payload=payload)
        payload = response.get('payload', {})
        raw_user = payload.get('contact')
        if raw_user:
            user = User.from_raw_data(raw_user)
        return user or response

    async def send_message(self, chat_id: int, cid: int, text: str, link: dict | None = None, elements: list[Element] = [], attaches: list[PhotoAttach | VideoAttach | FileAttach] = [], notify: bool = True) -> Message:
        message_instance = payloads.Message(cid=cid, text=text, link=link, elements=elements, attaches=attaches)
        message = message_instance.to_dict()
        payload_instance = payloads.SendMessage(chat_id=chat_id, message=message, notify=notify)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.SEND_MESSAGE, payload=payload)
        payload = response.get('payload', {})
        chat_id = payload.get('chatId')
        raw_message = payload.get('message')
        if raw_message:
            message = Message.from_raw_data(raw_data=raw_message, chat_id=chat_id, client=self)
        return message

    async def delete_message(self, chat_id: int, message_ids: list[int], for_me: bool = True) -> dict:
        payload_instance = payloads.DeleteMessage(chat_id=chat_id, message_ids=message_ids, for_me=for_me)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.DELETE_MESSAGE, payload=payload)
        return response

    async def edit_message(self, chat_id: int, message_id: int, text: str, elements: list[Element] = [], attaches: list = [PhotoAttach | VideoAttach | FileAttach]) -> Message:
        payload_instance = payloads.EditMessage(chat_id=chat_id, message_id=message_id, text=text, elements=elements, attaches=attaches)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.EDIT_MESSAGE, payload=payload)
        payload = response.get('payload', {})
        raw_message = payload.get('message')
        if raw_message:
            message = Message.from_raw_data(raw_data=raw_message, chat_id=chat_id)
        return message

    async def create_group(self, cid: int, title: str, user_ids: list[int] = [], notify: bool = True) -> Chat:
        attaches_instance = payloads.NewGroup(title=title, user_ids=user_ids)
        attaches = [attaches_instance.to_dict()]
        message_instance = payloads.Message(cid=cid, text=None, link=None, elements=[], attaches=attaches)
        message = message_instance.to_dict()
        payload_instance = payloads.SendMessage(chat_id=None, message=message, notify=notify)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.SEND_MESSAGE, payload=payload)
        payload = response.get('payload', {})
        raw_chat = payload.get('chat')
        if raw_chat:
            chat = Chat.from_raw_data(raw_data=raw_chat, client=self)
        return chat

    async def delete_chat(self, id, for_all: bool = True) -> dict:
        payload_instance = payloads.DeleteChat(chat_id=id, for_all=for_all)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.DELETE_CHAT, payload=payload)
        return response

    async def update_chat_members(self, chat_id: int, operation: str, user_ids: list[int], show_history: bool = True) -> dict:
        payload_instance = payloads.UpdateChatMembers(chat_id=chat_id, operation=operation, user_ids=user_ids, show_history=show_history)
        payload = payload_instance.to_dict()

        response = await self.do_api_request(opcode=Opcode.CHAT_MEMBERS_UPDATE, payload=payload)
        return response

    async def close_all_sessions(self) -> dict:
        response = await self.do_api_request(opcode=Opcode.SESSIONS_CLOSE, payload={})
        return response