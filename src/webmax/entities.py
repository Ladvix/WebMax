from .static import AccessType, ChatType, ElementType, MessageStatus, MessageType

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
    def from_raw_data(cls, raw_data: dict[str]) -> 'Element':
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

    def __repr__(self) -> str:
        return (
            f'Element(type={self.type!r}, length={self.length!r}, entity_id={self.entity_id!r}, attributes={self.attributes!r})'
        )

    def __str__(self) -> str:
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
    def from_raw_data(raw_data: dict[str]) -> 'MessageLink':
        chat_id = raw_data.get('chatId')
        message_id = raw_data.get('messageId')
        type = raw_data.get('type')

        return MessageLink(
            chat_id=chat_id,
            message_id=message_id,
            type=type
        )

    def __repr__(self) -> str:
        return f'MessageLink(chat_id={self.chat_id!r}, message_id={self.message_id!r}, type={self.type!r})'

    def __str__(self) -> str:
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
    def from_raw_data(cls, raw_data: dict[str], chat_id: int | None = None, client=None) -> 'Message':
        id = raw_data.get('id')
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

    async def reply(self, text: str, cid: int, elements: list[Element] | None = None, attaches: list[PhotoAttach | VideoAttach | FileAttach] | None = None) -> 'Message':
        link = {
            'type': 'REPLY',
            'messageId': self.id
        }
        message = await self.client.send_message(chat_id=self.chat_id, cid=cid, text=text, link=link, elements=elements, attaches=attaches)
        return message

    async def delete(self, for_me: bool | None = None) -> dict:
        return await self.client.delete_message(chat_id=self.chat_id, message_ids=[self.id], for_me=for_me)

    def __repr__(self) -> str:
        return f'<Message(sender_id={self.sender_id!r}, text={self.text!r})>'

    def __str__(self) -> str:
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
    def from_raw_data(cls, raw_data: dict[str]) -> 'User':
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

    def __repr__(self) -> str:
        return f'User(id={self.id!r}, first_name={self.firstname!r}, last_name={self.lastname!r}, status={self.account_status!r})'
    
    def __str__(self) -> str:
        full_name = f'{self.firstname} {self.lastname}'.strip()
        return f'User {self.id}: {full_name}'

class Chat:
    def __init__(
        self,
        participants_count: int,
        access: AccessType,
        type: ChatType,
        last_fire_delayed_error_time: int,
        last_delayed_update_time: int,
        options: dict[str, bool],
        modified: int,
        id: int,
        admin_participants: dict[int, dict],
        participants: dict[int],
        owner: int,
        join_time: int,
        created: int,
        last_event_time: int,
        messages_count: int,
        admins: list[int],
        status: str,
        cid: int,
        restrictions: int | None = None,
        title: str | None = None,
        last_message: Message | None = None,
        prev_message_id: str | None = None,
        base_raw_icon_url: str | None = None,
        base_icon_url: str | None = None,
        description: str | None = None,
        invited_by: int | None = None,
        link: str | None = None
    ):
        self.id = id
        self.participants_count = participants_count
        self.access = access
        self.invited_by = invited_by
        self.link = link
        self.type = type
        self.title = title
        self.last_fire_delayed_error_time = last_fire_delayed_error_time
        self.last_delayed_update_time = last_delayed_update_time
        self.options = options
        self.base_raw_icon_url = base_raw_icon_url
        self.base_icon_url = base_icon_url
        self.description = description
        self.modified = modified
        self.admin_participants = admin_participants or []
        self.participants = participants or []
        self.owner = owner
        self.join_time = join_time
        self.created = created
        self.last_message = last_message
        self.prev_message_id = prev_message_id
        self.last_event_time = last_event_time
        self.messages_count = messages_count
        self.admins = admins or []
        self.restrictions = restrictions
        self.status = status
        self.cid = cid

    @classmethod
    def from_raw_data(cls, raw_data: dict[str]) -> 'Chat':
        id = raw_data.get('id')
        participants_count = raw_data.get('participantsCount')
        access = raw_data.get('access')
        type = raw_data.get('type')
        last_fire_delayed_error_time = raw_data.get('lastFireDelayedErrorTime')
        last_delayed_update_time = raw_data.get('lastDelayedUpdateTime')
        options = raw_data.get('options')
        modified = raw_data.get('modified')
        admin_participants = raw_data.get('adminParticipants')
        participants = raw_data.get('participants')
        admin_participants = raw_data.get('adminParticipants')
        owner = raw_data.get('owner')
        join_time = raw_data.get('joinTime')
        created = raw_data.get('created')
        last_event_time = raw_data.get('lastEventTime')
        messages_count = raw_data.get('messagesCount')
        created = raw_data.get('created')
        admins = raw_data.get('admins')
        status = raw_data.get('status')
        cid = raw_data.get('cid')
        restrictions = raw_data.get('restrictions')
        title = raw_data.get('title')
        last_message = raw_data.get('lastMessage')
        prev_message_id = raw_data.get('prevMessageId')
        base_raw_icon_url = raw_data.get('baseRawIconUrl')
        base_icon_url = raw_data.get('baseIconUrl')
        description = raw_data.get('description')
        invited_by = raw_data.get('invitedBy')
        link = raw_data.get('link')

        return Chat(
            id=id,
            participants_count=participants_count,
            access=access,
            type=type,
            last_fire_delayed_error_time=last_fire_delayed_error_time,
            last_delayed_update_time=last_delayed_update_time,
            options=options,
            modified=modified,
            admin_participants=admin_participants,
            participants=participants,
            owner=owner,
            join_time=join_time,
            created=created,
            last_event_time=last_event_time,
            messages_count=messages_count,
            admins=admins,
            status=status,
            cid=cid,
            restrictions=restrictions,
            title=title,
            last_message=last_message,
            prev_message_id=prev_message_id,
            base_raw_icon_url=base_raw_icon_url,
            base_icon_url=base_icon_url,
            description=description,
            invited_by=invited_by,
            link=link
        )
    
    def __repr__(self) -> str:
        return f'Chat(id={self.id!r}, title={self.title!r}, type={self.type!r})'

    def __str__(self) -> str:
        return f'Chat {self.title}/{self.id} ({self.type})'

class ChatAction():
    def __init__(
        self,
        type: str,
        chat: Chat,
        user: User
    ):
        self.type = type
        self.chat = chat
        self.user = user