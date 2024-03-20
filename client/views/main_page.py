import flet as ft
from client1.tools.CryptoRSA import Crypto
import hashlib
import os
import sqlite3
import asyncio
import threading
import nest_asyncio
import random
from client1.views.chat_window import chat


def main(connector, db, page):

    def send_invite(user_id, public_key, user_name, status):
        our_id = db.get_my_id()[0]
        if status == "newinvite":
            our_public_key, our_private_key = Crypto().generate_keys()

            find = connector.find_user(new_task.value)

            data = {"from_id": our_id, "to_id": find["user"]["user_id"], "public_key": our_public_key, "status": status}
            send = connector.send_invites(invites_data=data)
            if send["status"] == "ok":
                chat_id = random.randint(1000000, 9000000)
                db.add_contact(user_id=find["user"]["user_id"], public_key=None, our_private_key=our_private_key, nickname=find["user"]["user_name"], status="wait", chat_id=chat_id)
                search.controls.clear()
                search.controls.append(
                    ft.Row(
                        [
                            ft.Text(f"Приглашение было отправлено!")
                        ]

                    )
                )
        elif status == "accepted":
            our_public_key, our_private_key = Crypto().generate_keys()

            data = {"from_id": our_id, "to_id": user_id, "public_key": our_public_key,
                    "status": status}
            send = connector.send_invites(invites_data=data)
            if send["status"] == "ok":
                chat_id = random.randint(1000000, 9000000)
                db.add_contact(user_id=user_id, public_key=public_key, our_private_key=our_private_key,
                               nickname=user_name, status="friend", chat_id=chat_id)
                search.controls.clear()
                tasks_view.clean()
                tasks_view.controls.append(
                    ft.Row(
                        [
                            ft.Text(f"Пользователь был добавлен в друзья!")
                        ]

                    )
                )
                check_contacts()

        elif status == "unaccepted":
            our_public_key, our_private_key = Crypto().generate_keys()

            data = {"from_id": our_id, "to_id": user_id, "public_key": our_public_key,
                    "status": status}
            send = connector.send_invites(invites_data=data)
            if send["status"] == "ok":
                chat_id = random.randint(1000000, 9000000)
                db.add_contact(user_id=user_id, public_key=public_key, our_private_key=our_private_key,
                               nickname=user_name, status="blacklist", chat_id=None)
                search.controls.clear()
                tasks_view.controls.append(
                    ft.Row(
                        [
                            ft.Text(f"Приглашение отклонено!")
                        ]

                    )
                )

        new_task.value = ""

        page.update()


    def find_user(e):
        find = connector.find_user(new_task.value)

        if find["user"] != "0":
            search.controls.clear()
            search.controls.append(
                ft.Row(
                    [
                        ft.Text(f"Пользователь с никнеймом {new_task.value} найден!"),
                        ft.ElevatedButton("Отправить запрос", on_click=lambda _: send_invite(None, None, None, "newinvite"), style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=2),
                                                          bgcolor="#0064b1", color="WHITE"))
                    ]

                )
            )
        else:
            search.controls.clear()
            search.controls.append(ft.Row([ft.Text("Такого пользователя не существует")]))


        #new_task.value = ""
        view.update()


    async def get_new_invites(connector):
        my_id = db.get_my_id()[0]
        while True:
            invites = await connector.get_new_invites(from_user=my_id)
            if invites["invites"] != "0":
                for data in invites["invites"]:
                    if data["status"] == "newinvite":
                        tasks_view.controls.append(
                            ft.Container(
                                border=ft.border.all(3, ft.colors.RED),
                                content=
                                ft.Row([
                                    ft.Text(f"{data['text']} "),
                                    ft.ElevatedButton("Принять", on_click=lambda _: send_invite(data["from_user"], data["public_key"], data["user_name"], "accepted"),
                                                      style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=2),
                                                                           bgcolor="#0064b1", color="WHITE")),

                                    ft.ElevatedButton("Отказаться", on_click=lambda _: send_invite(data["from_user"], data["public_key"], data["user_name"], "unaccepted"),
                                                      style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=2),
                                                                           bgcolor="#0064b1", color="WHITE"))

                                ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                )
                            )
                        )
                        page.update()
                    elif data['status'] == "accepted":
                        db.update_contact(data["public_key"], "friend", data["from_user"])
                        tasks_view.clean()
                        check_contacts()
                    elif data['status'] == "unaccepted":
                        db.update_contact(None, None, data["from_user"])
                        page.update()


            await asyncio.sleep(5)

    def run_async_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(get_new_invites(connector))
        loop.run_forever()


    new_task = ft.TextField(hint_text="Поиск", expand=True)
    search = ft.Row([ft.Text()])
    tasks_view = ft.Column()


    def check_contacts():
        my_contacts = db.get_my_contacts()
        if my_contacts != []:
            for data in my_contacts:
                if data[5] == "friend":
                    tasks_view.controls.append(
                        ft.Container(
                            border=ft.border.all(3, ft.colors.BLUE),
                            content=
                            ft.Row([
                                ft.Text(f"@{data[4]} - ваш друг"),
                                ft.ElevatedButton("Написать", on_click=lambda _: page.go(f"/chat/{data[6]}"),
                                                  style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=2),
                                                                       bgcolor="#0064b1", color="WHITE"))

                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        )
                    )
                else:
                    tasks_view.controls.append(
                        ft.Container(
                            border=ft.border.all(3, ft.colors.BLUE),
                            content=
                            ft.Row([
                                ft.Text(f"@{data[4]} еще не принял ваш запрос", size=20, color=ft.colors.BLACK)

                                ]
                            )
                        )
                    )
        else:
            tasks_view.controls.append(
                ft.Row([
                    ft.Text("У вас нет контактов!")
                ])
            )

        page.update()

    check_contacts()
    t = threading.Thread(target=run_async_in_thread)
    t.start()

    view=ft.Column(
        width=600,
        controls=[
            ft.Row(
                controls=[
                    new_task,
                    ft.FloatingActionButton(icon=ft.icons.ADD, on_click=find_user),
                ],
            ),

            search,
            tasks_view,
        ],
    )

    return view

