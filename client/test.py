# # import os
# # import sqlite3
# #
# # def create_database_and_path(database_name):
# #     database_path = f'users/{database_name}'
# #
# #     if not os.path.exists(database_path):
# #         os.makedirs('users', exist_ok=True)
# #         conn = sqlite3.connect(database_path)
# #         conn.close()
# #         print(f'Создан путь {database_path} и база данных {database_name}')
# #     else:
# #         print(f'Путь {database_path} уже существует')
# #
# #
# # database_name = '1.db'
# # create_database_and_path(database_name)
#
# from flet import *
#
#
#
#
# def main(page: Page):
#     page.title = "Login app"
#     page.vertical_alignment = MainAxisAlignment.CENTER
#     page.horizontal_alignment = CrossAxisAlignment.CENTER
#
#     page.window_max_width = 1280
#     page.window_max_height = 720
#
#     server_connect = TextField(label="Соединение", color="BLACK", border_width=0.5, border_color="BLACK")
#
#
#
#
#
#
#
#
#
#     page.add(
#         Container(
#             border_radius=5,
#             bgcolor="#f4f5f8",
#             alignment=alignment.center,
#             height=720,
#             width=1280,
#             padding=0,
#             content=Card(
#                 color=colors.BLUE,
#                 elevation=10,
#                 content=Container(
#                     bgcolor=colors.WHITE,
#                     width=400,
#                     height=400,
#                     padding=20,
#                     alignment=alignment.center,
#                     content=Column(
#                         [
#                             Row([
#                                 Text("BeHappy v.01", font_family="MathSansBoldItalic", size=14, color="BLUE")
#                             ]),
#
#                             Row([
#                                 Text("Подключение к серверу", font_family="MathSansBoldItalic", size=28, color="BLACK", weight=FontWeight.BOLD),
#                             ], alignment=MainAxisAlignment.CENTER),
#
#                             Row([
#                                 Text("Если вы нашли или создали свой сервер,\nподключитесь к нему:",
#                                      font_family="MathSansBoldItalic", size=14, color="BLACK",
#                                      weight=FontWeight.BOLD)
#                             ], alignment=MainAxisAlignment.CENTER),
#
#                             Row([server_connect], alignment=MainAxisAlignment.CENTER),
#
#                             Row([ElevatedButton("Подключиться", on_click=connect,
#                                                 style=ButtonStyle(shape=RoundedRectangleBorder(radius=2),
#                                                                   bgcolor="#0064b1", color="WHITE"), width=300,
#                                                 height=70)], alignment=MainAxisAlignment.CENTER)
#                         ],
#                         alignment=MainAxisAlignment.SPACE_BETWEEN
#                     )
#
#                 )
#             )
#         )
#     )
#
# app(target=main)
#
#
#
#


from tools.generate_db import AccountGenerator

db = AccountGenerator("users/new.db")

print(db.get_contact(2089304))
