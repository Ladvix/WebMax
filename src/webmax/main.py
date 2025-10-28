import uuid
import asyncio
from typing import Callable, List, Dict, Any
from .database.db import Database
from . import payloads
from .api import ApiMixin
from .auth import AuthMixin
from .handlers import HandlersMixin
from .websocket import WebsocketMixin
from .utils import credentials_utils
from .exceptions import NotAuthorizedError

class WebMaxClient(ApiMixin, AuthMixin, WebsocketMixin, HandlersMixin):
    '''
    Клиент для работы с API Max по вебсокету.
    https://web.max.ru

    Args:
        phone (str = None): Номер телефона для авторизации (опционально, если пользователь уже авторизован).
        device_id (str = None): ID устройства (опционально).

    Raises:
        InvalidPhoneError: Неверный формат телефона.
        NotAuthorizedError: Пользователь не авторизован, при этом номер телефона не был получен.
        ConnectionError: Ошибка подключения в вебсокету.
        ApiError: Ошибка на строне API.
    '''

    def __init__(self, name: str, phone: str | None = None):
        self.name = name
        self.uri = 'wss://ws-api.oneme.ru/websocket'
        self.headers = {
            'origin': 'https://web.max.ru',
        }
        self.ver = 11
        self.seq = 0
        self.websocket = None
        self.me = None
        self.chats = {}
        self.contacts = {}
        self.phone = phone

        self.on_message_handlers: List[Callable[[Dict[str, Any]], None]] = []
        self.on_message_removed_handlers: List[Callable[[Dict[str, Any]], None]] = []
        self.on_chat_action_handlers: List[tuple[str, Callable]] = []
        self.on_start_handler: Callable[[], None] = None

        self._tasks = []
        self._recv_queue = asyncio.Queue()
        self._response_waiters: Dict[int, asyncio.Future] = {}

    async def start(self, device_name: str = 'Chrome', device_version: str = 'Linux'):
        '''
        Запускает клиент, подключается к вебсокету, авторизирует
        пользователя (если не авторизован) и запусает фоновые циклы.

        Args:
            device_name (str = 'Chrome'): Название устройства (по умолчанию Chrome).
            device_version (str = 'Linux'): Версия устройства (по умолчанию Linux).
        '''
        instance = payloads.UserAgent(os_version=device_version, device_name=device_name)
        self.user_agent = instance.to_dict()

        await self.connect_web_socket()

        self.db = Database(db_path=f'{self.name}.db')
        await self.db.init()

        credentials = await credentials_utils.read(self.db)
        device_id = credentials.get('device_id')
        phone = credentials.get('phone')
        token = credentials.get('token')

        receiver_task = asyncio.create_task(self.message_receiver(), name='MessageReceiver')
        self._tasks.append(receiver_task)

        if device_id and phone and token:
            self.device_id = device_id
            self.phone = phone
            self.token = token
            await self.init(device_id=self.device_id)
        else:
            if self.phone:
                self.device_id = str(uuid.uuid4())
                await self.init(device_id=self.device_id)
                await self.auth()
            else:
                raise NotAuthorizedError

        await self.login(token=self.token)

        if self.on_start_handler:
            if asyncio.iscoroutinefunction(self.on_start_handler):
                await self.on_start_handler()
            else:
                self.on_start_handler()

        action_task = asyncio.create_task(self.action_handler(), name='ActionHandler')
        ping_task = asyncio.create_task(self.ping_loop(), name='PingLoop')
        self._tasks = self._tasks + [action_task, ping_task]

        try:
            await asyncio.gather(*self._tasks)
        except asyncio.CancelledError:
            pass
        finally:
            for task in self._tasks:
                task.cancel()
            await asyncio.gather(*self._tasks, return_exceptions=True)