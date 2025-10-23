import time
import asyncio
from webmax import WebMaxClient
from webmax import Message
from webmax.entities import User

async def main():
    client = WebMaxClient(phone='+7')

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