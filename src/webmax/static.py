class ElementType():
    TEXT = 'TEXT'
    USER_MENTION = 'USER_MENTION'
    LINK = 'LINK'
    ANIMOJI = 'ANIMOJI'

class MessageType():
    USER = 'USER'
    SYSTEM = 'SYSTEM'
    SERVICE = 'SERVICE'

class MessageLinkType():
    REPLY = 'REPLY'

class MessageStatus():
    REMOVED = 'REMOVED'

class ChatType(str):
    DIALOG = 'DIALOG'
    CHAT = 'CHAT'
    CHANNEL = 'CHANNEL'

class AccessType(str):
    PUBLIC = 'PUBLIC'
    PRIVATE = 'PRIVATE'
    SECRET = 'SECRET'

class ChatActions():
    TYPING = 'TYPING'
    FILE = 'FILE'
    STICKER = 'STICKER'

class ContactActions():
    ADD = 'ADD'
    REMOVE = 'REMOVE'
    BLOCK = 'BLOCK'
    UNBLOCK = 'UNBLOCK'

class Constants():
    PHONE_REGEX = r'^\+?\d{10,15}$'

class Opcode():
    PING = 1
    INIT = 6
    CHANGE_PROFILE_DATA = 16
    AUTH_REQUEST = 17
    AUTH = 18
    LOGIN = 19
    LOG_OUT = 20
    CONTACT_INFO = 32
    CONTACT_UPDATE = 34
    DELETE_CHAT = 52
    SEND_MESSAGE = 64
    DELETE_MESSAGE = 66
    EDIT_MESSAGE = 67
    CHAT_MEMBERS_UPDATE = 77
    SESSIONS_CLOSE = 97
    NOTIF_MESSAGE = 128
    NOTIF_CHAT_ACTION = 129