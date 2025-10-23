import time
from .static import ElementType, MessageStatus, MessageType

class Element:
    def __init__(
        self,
        type: ElementType,
        length: int,
        entity_id: int,
        attributes: dict
    ):
        self.type = type
        self.length = length
        self.entity_id = entity_id
        self.attributes = attributes

    @classmethod
    def from_raw_data(cls, raw_data: dict[str]):
        type = raw_data.get('type')
        length = raw_data.get('length')
        entity_id = raw_data.get('entityId')
        attributes = raw_data.get('attributes')

        return Element(
            type=type,
            length=length,
            entity_id=entity_id,
            attributes=attributes
        )

    def __repr__(self):
        return (
            f'Element(type={self.type!r}, length={self.length!r}, entity_id={self.entity_id!r}, attributes={self.attributes!r})'
        )

    def __str__(self):
        return f'Element {self.entity_id}: {self.type}'

class ReactionInfo:
    def __init__(
        self
    ):
        pass

class PhotoAttach:
    def __init__(
        self
    ):
        pass

class VideoAttach:
    def __init__(
        self
    ):
        pass

class FileAttach:
    def __init__(
        self
    ):
        pass

class MessageLink:
    def __init__(
        self,
        chat_id: int,
        message_id: int,
        type: str
    ):
        self.chat_id = chat_id
        self.message_id = message_id
        self.type = type

    @staticmethod
    def from_raw_data(raw_data: dict[str]):
        chat_id = raw_data.get('chatId')
        message_id = raw_data.get('messageId')
        type = raw_data.get('type')

        return MessageLink(
            chat_id=chat_id,
            message_id=message_id,
            type=type
        )

    def __repr__(self):
        return f'MessageLink(chat_id={self.chat_id!r}, message_id={self.message_id!r}, type={self.type!r})'

    def __str__(self):
        return f'MessageLink of message {self.message_id} from {self.chat_id}: {self.type}'

class Message:
    def __init__(
        self,
        client,
        sender_id: int,
        reaction_info: ReactionInfo,
        id: str,
        time: int,
        text: str,
        type: MessageType,
        raw_data: dict,
        chat_id: int | None = None,
        options: list[str] | None = None,
        link: MessageLink | None = None,
        status: MessageStatus | None = None,
        elements: list[Element] | None = None,
        attaches: list[PhotoAttach | VideoAttach | FileAttach] | None = None
    ):
        self.client = client
        self.chat_id = chat_id
        self.sender_id = sender_id
        self.elements = elements or []
        self.options = options or []
        self.id = id
        self.time = time
        self.text = text
        self.type = type
        self.attaches = attaches or []
        self.status = status
        self.link = link
        self.reaction_info = reaction_info
        self.raw_data = raw_data

    @classmethod
    def from_raw_data(cls, raw_data: dict[str], client=None):
        id = raw_data.get('id')
        chat_id = raw_data.get('chat_id')
        text = raw_data.get('text')
        sender_id = raw_data.get('sender')
        status = raw_data.get('status')
        type_ = raw_data.get('type')
        time = raw_data.get('time')
        attaches = raw_data.get('attaches')
        reaction_info = raw_data.get('reaction_info')
        options = raw_data.get('options')
        raw_elements = raw_data.get('elements')
        elements = []
        if raw_elements:
            for element in raw_elements:
                elements.append(Element.from_raw_data(element))
        link = raw_data.get('link')
        if link:
            link = MessageLink.from_raw_data(link)

        return Message(
            client=client,
            chat_id=chat_id,
            sender_id=sender_id,
            elements=elements,
            reaction_info=reaction_info,
            options=options,
            id=id,
            time=time,
            link=link,
            text=text,
            status=status,
            type=type_,
            attaches=attaches,
            raw_data=raw_data
        )

    async def reply(self, text: str, cid: int, elements: list[Element] | None = None, attaches: list[PhotoAttach | VideoAttach | FileAttach] | None = None):
        link = {
            'type': 'REPLY',
            'messageId': self.id
        }
        await self.client.send_message(chat_id=self.chat_id, cid=cid, text=text, link=link, elements=elements, attaches=attaches)

    def __repr__(self):
        return f'<Message(sender_id={self.sender_id!r}, text={self.text!r})>'

    def __str__(self):
        return f'Message {self.id} from {self.sender_id}: {self.text}'

class User:
    def __init__(
        self,
        account_status: int,
        update_time: int,
        id: int,
        firstname: str,
        lastname: str,
        options: list[str] | None = None,
        base_url: str | None = None,
        base_raw_url: str | None = None,
        photo_id: int | None = None,
        description: str | None = None,
        gender: int | None = None,
        link: str | None = None,
        web_app: str | None = None,
        menu_button: dict[str] | None = None
    ):
        self.account_status = account_status
        self.update_time = update_time
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.options = options or []
        self.base_url = base_url
        self.base_raw_url = base_raw_url
        self.photo_id = photo_id
        self.description = description
        self.gender = gender
        self.link = link
        self.web_app = web_app
        self.menu_button = menu_button

    @classmethod
    def from_raw_data(cls, raw_data: dict[str]):
        id = raw_data.get('id')
        names = raw_data.get('names', [{}])
        name_info = names[0] if names else {}
        firstname = name_info.get('firstName', '')
        lastname = name_info.get('lastName', '')
        options = raw_data.get('options', [])
        account_status = raw_data.get('accountStatus')
        update_time = raw_data.get('updateTime')
        description = raw_data.get('description')
        gender = raw_data.get('gender')
        link = raw_data.get('link')
        web_app = raw_data.get('web_app')
        menu_button = raw_data.get('menu_button', [])
        base_url = raw_data.get('base_url')
        base_raw_url = raw_data.get('base_raw_url')
        photo_id = raw_data.get('photo_id')

        return User(
            account_status=account_status,
            update_time=update_time,
            id=id,
            firstname=firstname,
            lastname=lastname,
            options=options,
            base_url=base_url,
            base_raw_url=base_raw_url,
            photo_id=photo_id,
            description=description,
            gender=gender,
            link=link,
            web_app=web_app,
            menu_button=menu_button
        )

    def __repr__(self):
        return f'User(id={self.id!r}, first_name={self.firstname!r}, last_name={self.lastname!r}, status={self.account_status!r})'
    
    def __str__(self):
        full_name = f'{self.firstname} {self.lastname}'.strip()
        return f'User {self.id}: {full_name}'