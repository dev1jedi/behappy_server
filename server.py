from fastapi import Depends
from fastapi import FastAPI, WebSocket
from sqlalchemy.orm import Session
from models import crud, schemas
from models.db import SessionLocal

import asyncio
import json

# Инициализация FastAPI
app = FastAPI()

# Функция для получения доступа к базе данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Словарь для хранения подключенных к websocket пользователей
connected_users = {}

# Маршруты и обработчики

# Обработчик маршрута для получения данных сервера
@app.get("/", response_model=schemas.ServerData)
async def main(db: Session = Depends(get_db)):
    info = crud.get_server_data(db=db)
    return info

# Обработчик маршрута для поиска пользователя по имени
@app.get("/find_user/{user_name}")
async def fnd_user(user_name: str, db: Session = Depends(get_db)):
    user_data = crud.find_by_nickname(db=db, user_name=user_name)
    if user_data is not None:
        return {"user": user_data}
    else:
        return {"user": "0"}

# Обработчик маршрута для отправки приглашений
@app.post('/send_invites')
def upload_key(keys: schemas.ExchangeKeys, db: Session = Depends(get_db)):
    if keys.status == "newinvite" or keys.status == "accepted" or keys.status == "unaccepted":
        crud.add_key(db=db, add_data=keys)
        return {"status": "ok"}
    else:
        return {"status": "Incorrect status type"}

# Обработчик маршрута для получения новых приглашений
@app.get('/new_invites/{from_user}')
async def get_new_invites(from_user: str, db: Session = Depends(get_db)):
    if crud.check_invites(db=db, from_user=from_user):
        user_data = []

        invites = crud.get_invites(db=db, from_user=from_user)

        for data in invites:
            user_name = crud.get_user_name(db=db, user_id=data.from_id)

            if data.status == "accepted":
                data_text = {"from_user": data.from_id, "public_key": data.public_key, "text": f"Пользователь {user_name.user_name}, которому вы отправляли запрос, принял вас в друзья!", "status": "accepted", "user_name": user_name.user_name}
                user_data.append(data_text)
            elif data.status == "unaccepted":
                data_text = {"from_user": data.from_id, "text": f"Пользователь {user_name.user_name}, которому вы отправляли запрос, отклонил запрос", "status": "unaccepted", "user_name": user_name.user_name}
                user_data.append(data_text)
            elif data.status == "newinvite":
                data_text = {"from_user": data.from_id, "public_key": data.public_key, "text": f"Пользователь {user_name.user_name} хочет добавить вас", "status": "newinvite", "user_name": user_name.user_name}
                user_data.append(data_text)
        return {"invites": user_data}
    else:
        return {"invites": "0"}

# Обработчик регистрации на сервере
@app.post('/register')
async def register(data: schemas.Users, db: Session = Depends(get_db)):
    return crud.register_on_server(db=db, add_data=data)

# Обработчик отправки сообщения
@app.post('/send_message')
async def send(message: schemas.Message, db: Session = Depends(get_db)):
    print(message.message)
    return crud.add_message(db=db, add_message=message)


# Функция для проверки новых сообщений и отправки их через WebSocket
async def check_for_new_data(user_id: str, websocket: WebSocket, db):
    new_data = crud.get_messages(db=db, user_id=user_id)

    if new_data is not None:
        if len(new_data) < 11:
            messages = []
            for data in new_data:
                messages.append({"from_id": data.from_id, "message": data.message, "timestamp": data.timestamp})
            await websocket.send_text(json.dumps({"messages": messages}))
        else:
            count_of_messages = 0
            for data in new_data:
                messages = []
                if count_of_messages < 11:
                    messages.append({"from_id": data.from_id, "message": data.message, "timestamp": data.timestamp})
                    count_of_messages += 1
                else:
                    count_of_messages = 0
                    await websocket.send_text(json.dumps({"messages": messages}))
                    messages.clear()

    else:
        await websocket.send_text(json.dumps({"messages": "0"}))

# WebSocket-маршрут для обработки сообщений
@app.websocket("/ws/{user_id}")
async def get_messages_websocket(user_id: str, websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    connected_users[user_id] = websocket

    while True:
        await check_for_new_data(user_id, websocket, db=db)
        await asyncio.sleep(1)
