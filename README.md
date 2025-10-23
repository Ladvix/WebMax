<p align="center">
    <img src="assets/logo.png" alt="WebMax" width="150">
</p>

<p align="center">
    <strong>Python библиотека для взаимодействия с API мессенджера Max</strong>
</p>

> <h3><strong>Дисклеймер</strong></h3>
> 
> *   Это **неофициальная** библиотека для работы с API мессенджера Max.
> *   Использование может **нарушать условия предоставления услуг** сервиса.
> *   **Вы используете её исключительно на свой страх и риск.**
> *   **Мы не несём никакой ответственности** за любые последствия использования этого пакета, включая, но не ограничиваясь: блокировку аккаунтов, утерю данных, юридические риски и любые другие проблемы.

## Описание

**`webmax`** — асинхронная Python библиотека для работы с API мессенджера Max. Предоставляет возможность взаимодействовать с Max через WebSocket соединение.

### Базовый пример

```python
import time
import asyncio
from webmax import WebMaxClient
from webmax import Message
from webmax.entities import User

async def main():
    client = WebMaxClient(phone='+1234567890')

    @client.on_start()
    async def start():
        print(client.me)

    @client.on_message()
    async def handle_message(message: Message):
        if message.sender_id != client.me.id:
            try:
                sender = client.contacts[message.sender_id]
                await message.reply(text=f'Привет, {sender.firstname}. Сейчас я занят, отвечу позже', cid=int(time.time()))
            except:
                pass

    @client.on_message_removed()
    async def handle_message_removed(message: Message):
        print(message)

    @client.on_typing()
    async def handle_typing(chat_id: int, user: User):
        print(f'Пользователь {user.firstname} печатает вам сообщение...')

    await client.start()

asyncio.run(main())
```



