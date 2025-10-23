import json
import asyncio
import websockets
from .entities import Message
from .exceptions import ApiError
from .static import MessageStatus, Opcode

class WebsocketMixin():
    def __init__(self):
        pass

    async def connect_web_socket(self):
        try:
            self.websocket = await websockets.connect(self.uri, additional_headers=self.headers)
        except Exception as e:
            raise ConnectionError(f'Ошибка подключения. {e}')

    async def message_receiver(self):
        '''
        Получает и обрабатывает входящие сообщения от вебсокета.
        '''
        while True:
            try:
                raw_response = await self.websocket.recv()
                response = json.loads(raw_response)
                seq = response.get('seq')

                if seq is not None and seq in self._response_waiters:
                    future = self._response_waiters.pop(seq)
                    if not future.done():
                        future.set_result(response)
                else:
                    await self._recv_queue.put(response)
            except websockets.ConnectionClosedError:
                pass

    async def action_handler(self):
        '''
        Обрабатывает входящие и исходящие события.
        '''
        while True:
            try:
                response = await self._recv_queue.get()
                cmd = response.get('cmd')
                opcode = response.get('opcode')
                payload = response.get('payload', {})

                if opcode == Opcode.NOTIF_MESSAGE:
                    await self.notif_message(payload)
                elif opcode == Opcode.NOTIF_TYPING:
                    await self.notif_typing(payload)
            except asyncio.CancelledError:
                break

    async def notif_message(self, payload):
        raw_data = payload.get('message', {})
        chat_id = payload.get('chatId')
        raw_data['chat_id'] = chat_id
        message = Message.from_raw_data(raw_data, self)

        if not (message.sender_id in self.contacts):
            await self.get_contacts_info(contact_ids=[message.sender_id])
        contact = self.contacts.get(message.sender_id)

        if message.status == MessageStatus.REMOVED:
            for handler in self.on_message_removed_handlers:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
        else:
            for handler in self.on_message_handlers:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)

    async def notif_typing(self, payload):
        chat_id = payload.get('chatId')
        user_id = payload.get('userId')

        if not (user_id in self.contacts):
            await self.get_contacts_info(contact_ids=[user_id])
        user = self.contacts.get(user_id)

        for handler in self.on_typing_handlers:
            if asyncio.iscoroutinefunction(handler):
                await handler(chat_id=chat_id, user=user)
            else:
                handler(chat_id=chat_id, user=user)

    async def ping_loop(self):
        '''
        Запускает фоновый цикл ping запросов,
        чтобы избежать разрыва соединения
        '''
        while True:
            await self.ping()
            await asyncio.sleep(60)

    async def do_api_request(self, opcode: int, payload: dict):
        '''
        Выполняет стандартный запрос к API по вебсокету.
        '''
        if self.websocket is None:
            raise ConnectionError('Вебсокет не подключен')

        message = {
            'ver': self.ver,
            'cmd': 0,
            'seq': self.seq,
            'opcode': opcode,
            'payload': payload
        }

        future = asyncio.Future()
        self._response_waiters[self.seq] = future

        await self.websocket.send(json.dumps(message))
        expected_seq = self.seq
        self.seq += 1

        try:
            response = await future
            cmd = response.get('cmd')
            seq = response.get('seq')
            opcode = response.get('opcode')
            payload = response.get('payload', {})

            if cmd == 1 and seq == expected_seq:
                return response
            elif cmd == 3:
                error_message = payload.get('localizedMessage', 'Unknown error')
                error_type = payload.get('error', 'Unknown error type')
                raise ApiError(f'{error_message} ({error_type})')
        except asyncio.CancelledError:
            if expected_seq in self._response_waiters:
                del self._response_waiters[expected_seq]
            raise