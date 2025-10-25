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
        if message.sender_id != client.me.id:
            try:
                sender = client.contacts[message.sender_id]
                await message.reply(text=f'Привет, {sender.firstname}. Сейчас я занят, отвечу позже', cid=int(time.time()))
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