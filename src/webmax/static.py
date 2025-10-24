class ElementType():
    TEXT = 'TEXT'
    USER_MENTION = 'USER_MENTION'
    LINK = 'LINK'
    ANIMOJI = 'ANIMOJI'

class MessageType():
    USER = 'USER'
    SYSTEM = 'SYSTEM'
    SERVICE = 'SERVICE'

class MessageStatus():
    REMOVED = 'REMOVED'

class ChatActions():
    TYPING = 'typing'

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
    SEND_MESSAGE = 64
    DELETE_MESSAGE = 66
    EDIT_MESSAGE = 67
    NOTIF_MESSAGE = 128
    NOTIF_TYPING = 129