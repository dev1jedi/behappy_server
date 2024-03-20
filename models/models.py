from sqlalchemy import Boolean, Column, Integer, String, Float, MetaData

from .db import Base

metadata = MetaData()


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    online_status = Column(Boolean, nullable=True)


class ExchangeKeys(Base):
    __tablename__ = "exchangekeys"

    id = Column(Integer, primary_key=True)
    from_id = Column(String, nullable=False)
    to_id = Column(String, nullable=False)
    public_key = Column(String, nullable=False)
    status = Column(String, nullable=False)


class Messages(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    from_id = Column(String, nullable=False)
    to_id = Column(String, nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(Float, nullable=False)


class ServerData(Base):
    __tablename__ = "server_data"

    id = Column(Integer, primary_key=True)
    server_name = Column(String, nullable=False)
    server_ip = Column(String, nullable=True)
    server_port = Column(String, nullable=True)
    server_description = Column(String, nullable=True)
    user_amount = Column(Integer, nullable=False)
