<p align="center">
    <img src="assets/logo.png" alt="WebMax" width="150">
</p>

<h1 align="center">
    <strong>WebMax</strong>
</h1>

<p align="center">
    <img src="https://img.shields.io/badge/python-3.10+-3776AB.svg" alt="Python 3.11+">
    <img src="https://img.shields.io/badge/License-MIT-2f9872.svg" alt="License: MIT">
</p>

> <h3><strong>Дисклеймер</strong></h3>
> 
> *   Это **неофициальная** библиотека для работы с API мессенджера Max.
> *   Использование может **нарушать условия предоставления услуг** сервиса.
> *   **Вы используете её исключительно на свой страх и риск.**
> *   **Мы не несём никакой ответственности** за любые последствия использования этого пакета, включая, но не ограничиваясь: блокировку аккаунтов, утерю данных, юридические риски и любые другие проблемы.

## Описание

**`webmax`** — асинхронная Python библиотека для работы с API мессенджера Max. Позволяет взаимодействовать с Max через WebSocket соединение. Данная библиотека может быть использована для разработки юзерботов.

## Базовый пример

```python
import time
import asyncio
from webmax import WebMaxClient
from webmax.static import ChatActions
from webmax.entities import Message, ChatAction

async def main():
    client = WebMaxClient(phone='+1234567890')

    @client.on_start()
    async def start():
        print(client.me)

    @client.on_message()
    async def handle_message(message: Message):
        if message.sender.id != client.me.id:
            try:
                await message.reply(text=f'Привет, {message.sender.firstname}. Сейчас я занят, отвечу позже', cid=int(time.time()))
            except:
                pass

    @client.on_message_removed()
    async def handle_message_removed(message: Message):
        print(message.text)

    @client.on_chat_action()
    async def handle_chat_action(action: ChatAction):
        if action.type == ChatActions.TYPING:
            print(f'Пользователь {action.user.firstname} печатает вам сообщение')

    await client.start()

asyncio.run(main())
```