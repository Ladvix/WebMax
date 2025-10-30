import re
from dataclasses import dataclass, field, fields, is_dataclass

def snake_to_camel(name: str):
    if name.startswith('_'):
        return name
    return re.sub(r'_([a-z])', lambda m: m.group(1).upper(), name)

def as_camel_dict(obj):
    if is_dataclass(obj):
        result = {}
        for field in fields(obj):
            value = getattr(obj, field.name)
            key = snake_to_camel(field.name)
            result[key] = as_camel_dict(value)
        return result
    elif isinstance(obj, list):
        return [as_camel_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: as_camel_dict(v) for k, v in obj.items()}
    else:
        return obj

@dataclass
class Ping():
    interactive: bool = True

    def to_dict(self) -> dict:
        return as_camel_dict(self)

@dataclass
class NavigationEventParams():
    action_id: int
    screen_to: int
    screen_from: int
    source_id: int
    session_id: int

@dataclass
class NavigationEventPayload():
    event: str
    time: int
    user_id: int
    params: NavigationEventParams
    type: str = 'NAV'

@dataclass
class NavigationPayload():
    events: list[NavigationEventPayload]

@dataclass
class UserAgent:
    os_version: str
    device_name: str
    device_type: str = 'WEB'
    locale: str = 'ru'
    device_locale: str = 'ru'
    header_user_agent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    app_version: str = '25.10.5'
    screen: str = '1080x1920 1.0x'
    timezone: str = 'Europe/Moscow'

    def to_dict(self) -> dict:
        return as_camel_dict(self)

@dataclass
class Init():
    device_id: str
    user_agent: UserAgent = field(default_factory=UserAgent)

    def to_dict(self) -> dict:
        return as_camel_dict(self)

@dataclass
class ChangeProfileData():
    firstname: str
    lastname: str
    description: str

    def to_dict(self) -> dict:
        return as_camel_dict(self)

@dataclass
class AuthRequest():
    phone: str
    type: str
    language: str = 'ru'

    def to_dict(self) -> dict:
        return as_camel_dict(self)

@dataclass
class Auth():
    token: str
    verify_code: str
    auth_token_type: str = 'CHECK_CODE'

    def to_dict(self) -> dict:
        return as_camel_dict(self)

@dataclass
class Login():
    token: str
    interactive: bool = True
    chats_sync: int = 0
    contacts_sync: int = 0
    presence_sync: int = 0
    drafts_sync: int = 0
    chats_count: int = 40

    def to_dict(self) -> dict:
        return as_camel_dict(self)

@dataclass
class LogOut():
    interactive: bool = True

    def to_dict(self) -> dict:
        return as_camel_dict(self)

@dataclass
class GetContactsInfo():
    contact_ids: list[int]

    def to_dict(self) -> dict:
        return as_camel_dict(self)

@dataclass
class ContactUpdate():
    contact_id: int
    action: str

    def to_dict(self) -> dict:
        return as_camel_dict(self)

@dataclass
class Element():
    type: str
    length: int
    entity_id: int
    attributes: dict

    def to_dict(self) -> dict:
        return as_camel_dict(self)
    
@dataclass
class PhotoAttach():
    def to_dict(self) -> dict:
        return as_camel_dict(self)
    
@dataclass
class VideoAttach():
    def to_dict(self) -> dict:
        return as_camel_dict(self)
    
@dataclass
class FileAttach():
    def to_dict(self) -> dict:
        return as_camel_dict(self)

@dataclass
class MessageLink:
    chat_id: int
    message_id: str
    type: str

@dataclass
class Message():
    text: str
    cid: int
    link: MessageLink
    elements: list[Element]
    attaches: list[PhotoAttach | VideoAttach | FileAttach]

    def to_dict(self) -> dict:
        return as_camel_dict(self)

@dataclass
class SendMessage():
    message: Message
    notify: str
    chat_id: int

    def to_dict(self) -> dict:
        return as_camel_dict(self)

@dataclass
class DeleteMessage():
    chat_id: int
    message_ids: list[int]
    for_me: bool = True

    def to_dict(self) -> dict:
        return as_camel_dict(self)

@dataclass
class EditMessage():
    chat_id: int
    message_id: int
    text: str
    elements: list
    attaches: list

    def to_dict(self) -> dict:
        return as_camel_dict(self)

@dataclass
class NewGroup():
    title: str
    user_ids: list[int]
    _type: str = 'CONTROL'
    event: str = 'new'
    chat_type: str = 'CHAT'

    def to_dict(self) -> dict:
        return as_camel_dict(self)

@dataclass
class DeleteChat():
    chat_id: int
    for_all: bool = True

    def to_dict(self) -> dict:
        return as_camel_dict(self)

@dataclass
class UpdateChatMembers():
    chat_id: int
    user_ids: list[int]
    operation: str
    show_history: bool = True

    def to_dict(self) -> dict:
        return as_camel_dict(self)

@dataclass
class CloseAllSessions():
    def to_dict(self) -> dict:
        return {}