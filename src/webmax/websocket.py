import os
import json
import asyncio
import websockets
from .static import MessageStatus, Opcode, ChatActions
from .entities import Message, ChatAction
from .exceptions import ApiError

class WebsocketMixin():
    async def connect_web_socket(self):
        try:
            self.websocket = await websockets.connect(self.uri, additional_headers=self.headers)
        except Exception as e:
            raise ConnectionError(f'Ошибка подключения. {e}')

    async def message_receiver(self):
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
        while True:
            try:
                response = await self._recv_queue.get()
                cmd = response.get('cmd')
                opcode = response.get('opcode')
                payload = response.get('payload', {})

                if opcode == Opcode.NOTIF_MESSAGE:
                    await self.notif_message(payload)
                elif opcode == Opcode.NOTIF_CHAT_ACTION:
                    await self.notif_chat_action(payload)
            except asyncio.CancelledError:
                break

    async def notif_message(self, payload: dict):
        raw_data = payload.get('message', {})
        chat_id = payload.get('chatId')
        raw_data['chat_id'] = chat_id
        message = Message.from_raw_data(raw_data=raw_data, chat_id=chat_id, client=self)

        chat = self.chats.get(chat_id)

        if message.sender is None:
            return

        if not (message.sender.id in self.contacts):
            await self.get_contacts_info(contact_ids=[message.sender.id])
        contact = self.contacts.get(message.sender.id)

        if message.status == MessageStatus.REMOVED:
            for handler in self.on_message_removed_handlers:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message=message)
                else:
                    handler(message=message)
        else:
            for handler in self.on_message_handlers:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message=message)
                else:
                    handler(message=message)

    async def notif_chat_action(self, payload: dict):
        type = payload.get('type')
        chat_id = payload.get('chatId')
        user_id = payload.get('userId')

        chat = self.chats.get(chat_id)

        if not (user_id in self.contacts):
            await self.get_contacts_info(contact_ids=[user_id])
        user = self.contacts.get(user_id)

        action = ChatAction(
            type=type or ChatActions.TYPING,
            chat=chat,
            user=user
        )

        for action_filter, handler in self.on_chat_action_handlers:
            if action_filter is None or action_filter == 'typing':
                if asyncio.iscoroutinefunction(handler):
                    await handler(action)
                else:
                    handler(action)

    async def ping_loop(self):
        while True:
            await self.ping()
            await asyncio.sleep(60)

    async def do_api_request(self, opcode: int, payload: dict):
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
                error_message = payload.get('localizedMessage', 'Неизвестная ошибка')
                error_type = payload.get('error', 'Неизвестный тип ошибки')
                if error_type == 'login.token':
                    os.remove(f'{self.session_name}.db')
                raise ApiError(f'{error_message} ({error_type})')
        except asyncio.CancelledError:
            if expected_seq in self._response_waiters:
                del self._response_waiters[expected_seq]
            raise