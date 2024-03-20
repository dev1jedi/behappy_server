import flet as ft
import threading
import asyncio
from datetime import datetime
from client1.tools.CryptoRSA import Crypto

import nest_asyncio

nest_asyncio.apply()


class Message():
    def __init__(self, user: str, text: str):
        self.user_name = user
        self.text = text

class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = "start"

        self.controls=[
                ft.CircleAvatar(
                    content=ft.Text(self.get_initials(message.user_name)),
                    color=ft.colors.BLACK,
                    bgcolor=self.get_avatar_color(message.user_name),
                ),
                ft.Column(
                    [
                        ft.Text(message.user_name, weight="bold"),
                        ft.Text(message.text, selectable=True, weight="bold", size=14),
                    ],
                    tight=True,
                    spacing=10,
                ),
            ]


    def get_initials(self, user_name: str):
        if user_name:
            return user_name[:1].capitalize()
        else:
            return "Unknown"  # or any default value you prefer

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.colors.AMBER,
            ft.colors.BLUE,
            ft.colors.BROWN,
            ft.colors.CYAN,
            ft.colors.GREEN,
            ft.colors.INDIGO,
            ft.colors.LIME,
            ft.colors.ORANGE,
            ft.colors.PINK,
            ft.colors.PURPLE,
            ft.colors.RED,
            ft.colors.TEAL,
            ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]


def chat(connector, db, chat_id, page):
    contact = db.get_contact(chat_id=chat_id)

    our_id = db.get_my_id()[0]

    user_id = contact[0]
    public_key = contact[1]
    our_private_key = contact[2]

    chat_2 = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True
    )
    new_message = ft.TextField(
        hint_text="Написать сообщение...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True
    )

    def send_message(e):
        dt = datetime.now()
        ts = datetime.timestamp(dt)

        crypted_message = Crypto().encrypt(new_message.value, our_public_key=public_key)

        data = {"from_id": our_id, "to_id": user_id, "message": crypted_message, "timestamp": ts}

        connector.send_message(data)

        db.add_message(user_id=our_id, text=crypted_message, timestamp=ts, chat_id=chat_id)

        user_name = db.get_username()[0]

        message = Message(user_name, new_message.value)
        m = ChatMessage(message)
        chat_2.controls.append(m)
        new_message.value = ""
        page.update()

    def get_messages():
        messages = db.get_messages(chat_id=chat_id)
        for message in messages:
            message = Message(message[1], message[2])
            m = ChatMessage(message)
            chat_2.controls.append(m)

    async def add_messages(decrypted_message):
        nickname = db.get_nickname(user_id)
        message = Message(nickname, decrypted_message)
        m = ChatMessage(message)
        chat_2.controls.append(m)
        page.update()

    async def get_new_messages(connector, chat_id: int):
        async for messages in connector.ws_handler(our_id):
            messages_data = messages["messages"]
            data = []
            if messages_data != "0":
                for message in messages_data:
                    decrypted_message = Crypto().decrypt(message["message"], our_private_key=our_private_key)
                    data.append((message['from_id'], decrypted_message, message["timestamp"], chat_id))

                    await add_messages(decrypted_message)

                await db.add_all_messages(data=data)
            await asyncio.sleep(1)

    def run_async_in_thread(connector, chat_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(get_new_messages(connector, chat_id=chat_id))
        loop.run_forever()


    get_messages()


    t = threading.Thread(target=run_async_in_thread, args=(connector, chat_id, ))
    t.start()

    view = [
            chat_2,
            ft.Row(
                [
                    new_message,
                    ft.IconButton(
                        icon=ft.icons.SEND_ROUNDED,
                        tooltip="Send message",
                        on_click=send_message
                    ),
                ]
            ),
            ]

    return view





