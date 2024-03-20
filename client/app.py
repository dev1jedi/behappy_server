from flet import *
from tools.generate_db import AccountGenerator
from tools.networker import MessengerClient
from tools.tools import validate_ip_port_domain
from tools.CryptoRSA import Crypto
from views.main_page import main
from views.chat_window import chat
import hashlib


import os
import sqlite3
import asyncio
import nest_asyncio
import random


nest_asyncio.apply()


class MainApp(UserControl):
    def __init__(self, page: Page):
        super().__init__()

        self.max_width = 650
        self.max_height = 720
        self.page = page

        page.title = "Be happy v.01"
        page.vertical_alignment = MainAxisAlignment.CENTER
        page.horizontal_alignment = CrossAxisAlignment.CENTER

        page.window_max_width = self.max_width
        page.window_max_height = self.max_height

        page.color = colors.WHITE
        page.theme_mode = "light"


        self.login = TextField(label="Логин", color="BLACK", border_width=0.5, border_color="BLACK")
        self.password = TextField(label="Пароль", color="BLACK", border_width=0.5, border_color="BLACK")
        self.server_connect = TextField(label="Соединение", color="BLACK", border_width=0.5, border_color="BLACK")

        self.connect_able = Row([ElevatedButton("Подключиться", on_click=self.connect,
                                                style=ButtonStyle(shape=RoundedRectangleBorder(radius=2),
                                                                  bgcolor="#0064b1", color="WHITE"), width=300,
                                                height=70)], alignment=MainAxisAlignment.CENTER)

        self.connect_text = Row([
            Text("Подключение к серверу", font_family="MathSansBoldItalic", size=28, color="BLACK",
                 weight=FontWeight.BOLD),
        ], alignment=MainAxisAlignment.CENTER)

        self.connect_description = Row([
            Text("Если вы нашли или создали свой сервер,\nподключитесь к нему:",
                 font_family="MathSansBoldItalic", size=14, color="BLACK",
                 weight=FontWeight.BOLD)
        ], alignment=MainAxisAlignment.CENTER)

        self.server_nickname = TextField(label="Введите никнейм", color="BLACK", border_width=0.5, border_color="BLACK")

        self.connector = None
        self.db = None

        self.helper()


    def create_database_and_path(self, database_name):
        database_path = f'users/{database_name}.db'

        if not os.path.exists(database_path):
            os.makedirs('users', exist_ok=True)
            conn = sqlite3.connect(database_path)
            conn.close()
            return True
        else:
            return None

    def register(self, _):
        self.login.error_text = None
        self.password.error_text = None
        if not self.login.value:
            self.login.error_text = "Введите логин"
            self.page.update()
        if not self.password.value:
            self.password.error_text = "Введите пароль"
            self.page.update()
        if all([self.login.value, self.password.value]):
            login = self.login.value
            passwrd = self.password.value
            if self.create_database_and_path(login):
                creator = AccountGenerator(f'users/{login}.db')
                if creator.create_tables():
                    if creator.create_account(login=login, password=passwrd, user_name=None, server=None):
                        self.page.go("/connect_to_server")

            else:
                self.login.error_text = "Такой аккаунт уже создан! Авторизуйтесь!"
                self.page.update()

    def auth(self, _):
        self.login.error_text = None
        self.password.error_text = None
        if not self.login.value:
            self.login.error_text = "Введите логин"
            self.page.update()
        if not self.password.value:
            self.password.error_text = "Введите пароль"
            self.page.update()
        if all([self.login.value, self.password.value]):
            login = self.login.value
            passwrd = self.password.value
            database_path = f'users/{login}.db'

            if os.path.exists(database_path):
                db = AccountGenerator(f'users/{login}.db')
                if db.check_password(password=passwrd):
                    base_url = db.get_server()
                    self.connector = MessengerClient(base_url=base_url)
                    self.db = db
                    self.page.go("/main")



    def server_add(self, _):
        db = AccountGenerator(f'users/{self.login.value}.db')
        connector = MessengerClient(self.server_connect.value)
        my_id = db.get_my_id()[0]
        nickname = self.server_nickname.value

        registration_data = {"user_id": my_id, "user_name": nickname, "description": None, "online_status": None}
        register = connector.register(registration_data=registration_data)
        if register["status"] == "registered":
            self.server_nickname.error_text = "Такой пользователь уже есть"
            self.page.update()
        elif register["status"] == "Successful registered":
            db.add_server(nickname, self.server_connect.value)
            self.connector = connector
            self.db = db
            self.page.go("/main")


    def register_to_server(self):
        return Container(
            border_radius=5,
            bgcolor="#f4f5f8",
            alignment=alignment.center,
            height=self.max_height,
            width=self.max_width,
            padding=0,
            content=Card(
                color=colors.BLUE,
                elevation=10,
                content=Container(
                        bgcolor=colors.WHITE,
                        width=400,
                        height=400,
                        padding=20,
                        alignment=alignment.center,
                        content=Column(
                            [
                                Row([
                                    Text("BeHappy v.01", font_family="MathSansBoldItalic", size=14, color="BLUE")
                                ]),

                                Row([
                                    Text("Регистрация на сервере", weight=FontWeight.BOLD, size=14, color=colors.BLACK)

                                ],
                                    alignment=MainAxisAlignment.SPACE_BETWEEN),

                                Row(
                                    [
                                        Text("Если вы хотите подключиться к этому серверу, придумайте никнейм.\nТак пользователям данного сервера будет проще вас найти", weight=FontWeight.BOLD, size=10, color=colors.BLACK)
                                    ]
                                ),

                                Row([self.server_nickname], alignment=MainAxisAlignment.CENTER),


                                Row([ElevatedButton("Подключение", on_click=self.server_add,
                                                    style=ButtonStyle(shape=RoundedRectangleBorder(radius=2),
                                                                      bgcolor="#0064b1", color="WHITE"), width=300,
                                                    height=70)], alignment=MainAxisAlignment.CENTER)
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN
                        )

                    )
                )
            )


    def connect(self, _):
        valid = validate_ip_port_domain(self.server_connect.value)

        async def check_connection(connector):
            return await connector.get_server_data()

        if valid:
            connector = MessengerClient(self.server_connect.value)

            check_connection = asyncio.run(check_connection(connector))
            text = f"""
            Сервер работает!
            Имя сервера: {check_connection["server_name"]}
            IP сервера: {check_connection["server_ip"]}
            Порт сервера: {check_connection["server_port"]}
            Описание: {check_connection["server_description"]}
            Максимальное количество пользователей: {check_connection["user_amount"]}
            """


            self.connect_text.clean()
            self.connect_description.clean()
            self.connect_description.controls.append(Row([
                                    Text(text, font_family="MathSansBoldItalic", size=12, color="BLACK",
                                         weight=FontWeight.BOLD),
                                ], alignment=MainAxisAlignment.CENTER))


            self.connect_able.clean()

            self.connect_able.controls.append(Row([ElevatedButton("Подключиться", on_click=lambda _: self.page.go("/accept_connect"),
                                                    style=ButtonStyle(shape=RoundedRectangleBorder(radius=2),
                                                                      bgcolor="#0064b1", color="WHITE"), width=300,
                                                    height=70)], alignment=MainAxisAlignment.CENTER))


            self.page.update()

        else:
            self.server_connect.error_text = "Введенные данные не соответствуют формату"
            self.page.update()


    def connect_to_server(self):
        self.connect_page = Container(
            border_radius=5,
            bgcolor="#f4f5f8",
            alignment=alignment.center,
            height=720,
            width=1280,
            padding=0,
            content=Card(
                color=colors.BLUE,
                elevation=10,
                content=Container(
                    bgcolor=colors.WHITE,
                    width=400,
                    height=400,
                    padding=20,
                    alignment=alignment.center,
                    content=Column(
                        [
                            Row([
                                Text("BeHappy v.01", font_family="MathSansBoldItalic", size=14, color="BLUE")
                            ]),

                            self.connect_text,

                            self.connect_description,

                            Row([self.server_connect], alignment=MainAxisAlignment.CENTER),

                            self.connect_able
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN
                    )

                )
            )
        )
        return self.connect_page


    def create_login(self):
        self.main_container = Container(
            border_radius=5,
            bgcolor="#f4f5f8",
            alignment=alignment.center,
            height=self.max_height,
            width=self.max_width,
            padding=0,
            content=Card(
                color=colors.BLUE,
                elevation=10,
                content=Container(
                        bgcolor=colors.WHITE,
                        width=400,
                        height=400,
                        padding=20,
                        alignment=alignment.center,
                        content=Column(
                            [
                                Row([
                                    Text("BeHappy v.01", font_family="MathSansBoldItalic", size=14, color="BLUE")
                                ]),

                                Row([
                                    Text("Авторизация", weight=FontWeight.BOLD, size=14, color=colors.BLACK),
                                    ElevatedButton("Регистрация", on_click=lambda _: self.page.go("/register"),
                                                   style=ButtonStyle(shape=RoundedRectangleBorder(radius=0),
                                                                     bgcolor="#f4f5f8",
                                                                     color="BLUE"))
                                ],
                                    alignment=MainAxisAlignment.SPACE_BETWEEN),

                                Row([self.login], alignment=MainAxisAlignment.CENTER),

                                Row([self.password], alignment=MainAxisAlignment.CENTER),

                                Row([ElevatedButton("Login", on_click=self.auth,
                                                    style=ButtonStyle(shape=RoundedRectangleBorder(radius=2),
                                                                      bgcolor="#0064b1", color="WHITE"), width=300,
                                                    height=70)], alignment=MainAxisAlignment.CENTER)
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN
                        )

                    )
                )
            )
        return self.main_container


    def create_reg(self):
        self.main_container = Container(
            border_radius=5,
            bgcolor="#f4f5f8",
            alignment=alignment.center,
            height=self.max_height,
            width=self.max_width,
            padding=0,
            content=Card(
                color=colors.BLUE,
                elevation=10,
                content=Container(
                    bgcolor=colors.WHITE,
                    width=400,
                    height=400,
                    padding=20,
                    alignment=alignment.center,
                    content=Column(
                        [
                            Row([
                                Text("BeHappy v.01", font_family="MathSansBoldItalic", size=14, color="BLUE")
                            ]),

                            Row([
                                Text("Регистрация", weight=FontWeight.BOLD, size=14, color=colors.BLACK),
                                ElevatedButton("Авторизация", on_click=lambda _: self.page.go("/"),
                                               style=ButtonStyle(shape=RoundedRectangleBorder(radius=0),
                                                                 bgcolor="#f4f5f8",
                                                                 color="BLUE"))
                            ],
                                alignment=MainAxisAlignment.SPACE_BETWEEN),

                            Row([self.login], alignment=MainAxisAlignment.CENTER),

                            Row([self.password], alignment=MainAxisAlignment.CENTER),

                            Row([ElevatedButton("Создать аккаунт", on_click=self.register,
                                                style=ButtonStyle(shape=RoundedRectangleBorder(radius=2),
                                                                  bgcolor="#0064b1", color="WHITE"), width=300,
                                                height=70)], alignment=MainAxisAlignment.CENTER)],
                        alignment=MainAxisAlignment.SPACE_BETWEEN
                    )

                )
            )
        )
        return self.main_container


    def route_change(self, route):
        self.page.views.clear()
        self.page.views.append(
            View(
                "/",
                [
                    self.create_login()
                ],
                horizontal_alignment=CrossAxisAlignment.CENTER,
                vertical_alignment=MainAxisAlignment.CENTER

            )
        )
        if self.page.route == "/register":
            self.page.views.append(
                View(
                    "/register",
                    [
                        self.create_reg()
                    ],
                )
            )

        if self.page.route == "/connect_to_server":
            self.page.views.append(
                View(
                    "/connect_to_server",
                    [
                        self.connect_to_server()
                    ]
                )
            )

        if self.page.route == "/accept_connect":
            self.page.views.append(
                View(
                    "/accept_connect",
                    [
                        self.register_to_server()
                    ]
                )
            )

        if self.page.route == "/main":
            self.page.views.append(
                View(
                    "/main",
                    [main(self.connector, self.db, self.page)]
                )
            )

        troute = TemplateRoute(self.page.route)

        if troute.match("/chat/:id"):
            self.page.views.append(
                View(
                    "/chat",
                    [*chat(self.connector, self.db, troute.id, self.page)]
                )
            )

        self.page.update()


    def helper(self):
        self.page.on_route_change = self.route_change
        self.page.go(self.page.route)


if __name__ == "__main__":
    app(target=MainApp)

