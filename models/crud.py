from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import ServerData, ExchangeKeys, Users, Messages
from . import schemas


def get_server_data(db: Session):
    return db.query(ServerData).first()


def find_by_nickname(db: Session, user_name: str):
    item = db.query(Users).filter(Users.user_name == user_name).first()
    return item


def register_on_server(db: Session, add_data: schemas.Users):
    if db.scalar(select(Users).where(Users.user_id == add_data.user_id)):
        return {"status": "already registered"}

    if db.scalar(select(Users).where(Users.user_name == add_data.user_name)):
        return {"status": "registered"}

    new_data = Users(user_id=add_data.user_id, user_name=add_data.user_name, description=add_data.description, online_status=add_data.online_status)
    db.add(new_data)
    db.commit()
    return {"status": "Successful registered"}


def get_user_name(db: Session, user_id: str):
    item = db.query(Users).filter(Users.user_id == user_id).first()
    return item


def add_key(db: Session, add_data: schemas.ExchangeKeys):
    new_data = ExchangeKeys(from_id=add_data.from_id, to_id=add_data.to_id, public_key=add_data.public_key, status=add_data.status)
    db.add(new_data)
    db.commit()


def check_invites(db: Session, from_user: str):
    query = select(ExchangeKeys).where(ExchangeKeys.to_id == from_user)
    result = db.execute(query)
    if result.fetchone() is not None:
        return True
    else:
        return False

def get_invites(db: Session, from_user: str):
    items = db.query(ExchangeKeys).filter(ExchangeKeys.to_id == from_user).all()
    for item in items:
        db.delete(item)

    db.commit()
    return items


def add_message(db: Session, add_message: schemas.Message):
    new_data = Messages(from_id=add_message.from_id, to_id=add_message.to_id, message=add_message.message.replace("\x00", "\uFFFD"), timestamp=add_message.timestamp)
    db.add(new_data)
    db.commit()
    return {"status": "message was added"}


def get_messages(db: Session, user_id: str):
    query = select(Messages).where(Messages.to_id == user_id)
    result = db.execute(query)
    if result.fetchone() is not None:
        messages = db.query(Messages).filter(Messages.to_id == user_id).all()
        for item in messages:
            db.delete(item)

        db.commit()

        return messages
    else:
        return None
