from typing import Tuple
from . import payloads
from .utils import credentials_utils
from .static import ContactActions, Opcode
from .entities import Chat, Element, FileAttach, Message, PhotoAttach, User, VideoAttach

class ApiMixin():
    async def _send_call(self, opcode, payload):
        if type(payload) != dict:
            payload = payload.to_dict()
        response = await self.do_api_request(
            opcode=opcode,
            payload=payload
        )
        return response.get('payload', {})

    def get_chat_id(self, user_id):
        return self.me.id^user_id

    async def ping(self) -> dict:
        response_payload = await self._send_call(
            opcode=Opcode.PING,
            payload=payloads.Ping()
        )
        return response_payload

    async def init(self, device_id: str) -> dict:
        response_payload = await self._send_call(
            opcode=Opcode.INIT,
            payload=payloads.Init(
                user_agent=self.user_agent,
                device_id=device_id
            )
        )
        return response_payload

    async def change_profile_data(self, firstname: str | None = None, lastname: str | None = None, description: str | None = None) -> User:
        if not firstname:
            firstname = self.me.firstname
        if not lastname:
            lastname = self.me.lastname

        response_payload = await self._send_call(
            opcode=Opcode.CHANGE_PROFILE_DATA,
            payload=payloads.ChangeProfileData(
                firstname=firstname,
                lastname=lastname,
                description=description
            )
        )

        profile = response_payload.get('profile', {})
        raw_contact = profile.get('contact', {})
        self.me = User.from_raw_data(raw_data=raw_contact)
        self.contacts[self.me.id] = self.me

        return self.me

    async def send_code(self, phone: str) -> str:
        response_payload = await self._send_call(
            opcode=Opcode.AUTH_REQUEST,
            payload=payloads.AuthRequest(
                phone=phone,
                type='START_AUTH'
            )
        )

        temp_token = response_payload.get('token')
        return temp_token

    async def verify_code(self, code: str, token: str) -> str:
        response_payload = await self._send_call(
            opcode=Opcode.AUTH,
            payload=payloads.Auth(
                verify_code=code,
                token=token
            )
        )

        tokenAttrs = response_payload.get('tokenAttrs', {})
        login_data = tokenAttrs.get('LOGIN', {})
        token = login_data.get('token')
        profile = response_payload.get('profile', {})
        raw_contact = profile.get('contact')
        self.me = User.from_raw_data(raw_data=raw_contact)

        return token

    async def login(self, token: str) -> Tuple[User, list[Chat]]:
        response_payload = await self._send_call(
            opcode=Opcode.LOGIN,
            payload=payloads.Login(
                token=token
            )
        )

        chats = response_payload.get('chats', [])
        contacts = response_payload.get('contacts', [])

        for raw_chat in chats:
            chat = Chat.from_raw_data(raw_data=raw_chat, client=self)
            self.chats[chat.id] = chat

        for raw_contact in contacts:
            user = User.from_raw_data(raw_data=raw_contact)
            self.contacts[user.id] = user

        profile = response_payload.get('profile', {})
        raw_contact = profile.get('contact', {})
        self.me = User.from_raw_data(raw_data=raw_contact)
        self.contacts[self.me.id] = self.me

        return self.me, self.chats

    async def log_out(self) -> dict:
        response_payload = await self._send_call(
            opcode=Opcode.LOG_OUT,
            payload=payloads.LogOut()
        )
        return response_payload

    async def get_contacts_info(self, contact_ids: list[int]) -> list[User]:
        response_payload = await self._send_call(
            opcode=Opcode.CONTACT_INFO,
            payload=payloads.GetContactsInfo(
                contact_ids=contact_ids
            )
        )

        contacts = {}
        raw_contacts = response_payload.get('contacts', [])
        for contact in raw_contacts:
            user = User.from_raw_data(raw_data=contact)
            contacts[user.id] = user
            self.contacts[user.id] = user

        return contacts

    async def update_contact(self, contact_id: int, action: ContactActions) -> User:
        response_payload = await self._send_call(
            opcode=Opcode.CONTACT_UPDATE,
            payload=payloads.ContactUpdate(
                contact_id=contact_id,
                action=action
            )
        )

        raw_user = response_payload.get('contact')
        if raw_user:
            user = User.from_raw_data(raw_data=raw_user)
        return user or response_payload

    async def send_message(self, chat_id: int, cid: int, text: str, link: dict | None = None, elements: list[Element] = [], attaches: list[PhotoAttach | VideoAttach | FileAttach] = [], notify: bool = True) -> Message:
        response_payload = await self._send_call(
            opcode=Opcode.SEND_MESSAGE,
            payload=payloads.SendMessage(
                chat_id=chat_id,
                message=payloads.Message(
                    cid=cid,
                    text=text,
                    link=link,
                    elements=elements,
                    attaches=attaches
                ),
                notify=notify
            )
        )

        chat_id = response_payload.get('chatId')
        raw_message = response_payload.get('message')
        if raw_message:
            message = Message.from_raw_data(
                raw_data=raw_message,
                chat_id=chat_id,
                client=self
            )
            return message

    async def delete_message(self, chat_id: int, message_ids: list[int], for_me: bool = True) -> dict:
        response_payload = await self._send_call(
            opcode=Opcode.DELETE_MESSAGE,
            payload=payloads.DeleteMessage(
                chat_id=chat_id,
                message_ids=message_ids,
                for_me=for_me
            )
        )
        return response_payload

    async def edit_message(self, chat_id: int, message_id: int, text: str, elements: list[Element] = [], attaches: list[PhotoAttach | VideoAttach | FileAttach] = []) -> Message:
        response_payload = await self._send_call(
            opcode=Opcode.EDIT_MESSAGE,
            payload=payloads.EditMessage(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                elements=elements,
                attaches=attaches
            )
        )

        raw_message = response_payload.get('message')
        if raw_message:
            message = Message.from_raw_data(
                raw_data=raw_message,
                chat_id=chat_id,
                client=self
            )
            return message

    async def create_group(self, cid: int, title: str, user_ids: list[int] = [], notify: bool = True) -> Chat:
        response_payload = await self._send_call(
            opcode=Opcode.SEND_MESSAGE,
            payload=payloads.SendMessage(
                chat_id=None,
                message=payloads.Message(
                    cid=cid,
                    text=None,
                    link=None,
                    elements=[],
                    attaches=[
                        payloads.NewGroup(
                            title=title,
                            user_ids=user_ids
                        )
                    ]
                ),
                notify=notify
            )
        )

        raw_chat = response_payload.get('chat')
        if raw_chat:
            chat = Chat.from_raw_data(
                raw_data=raw_chat,
                client=self
            )
            return chat

    async def delete_chat(self, id, for_all: bool = True) -> dict:
        response_payload = await self._send_call(
            opcode=Opcode.DELETE_CHAT,
            payload=payloads.DeleteChat(
                chat_id=id,
                for_all=for_all
            )
        )
        return response_payload

    async def update_chat_members(self, chat_id: int, operation: str, user_ids: list[int], show_history: bool = True) -> dict:
        response_payload = await self._send_call(
            opcode=Opcode.CHAT_MEMBERS_UPDATE,
            payload=payloads.UpdateChatMembers(
                chat_id=chat_id,
                operation=operation,
                user_ids=user_ids,
                show_history=show_history
            )
        )
        return response_payload

    async def close_all_sessions(self, save_token: bool = True) -> bool:
        response_payload = await self._send_call(
            opcode=Opcode.SESSIONS_CLOSE,
            payload=payloads.CloseAllSessions()
        )

        if save_token:
            self.token = response_payload.get('token')
            await credentials_utils.save(db=self.db, device_id=self.device_id, token=self.token, phone=self.phone)
        return True