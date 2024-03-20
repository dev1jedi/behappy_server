from typing import Optional
from pydantic import BaseModel


class ServerData(BaseModel):
    server_name: str
    server_ip: Optional[str]
    server_port: Optional[str]
    server_description: Optional[str]
    user_amount: int

    class Config:
        orm_mode = True


class Users(BaseModel):
    user_id: str
    user_name: str
    description: Optional[str]
    online_status: Optional[bool]


class ExchangeKeys(BaseModel):
    from_id: str
    to_id: str
    public_key: str
    status: str

    class Config:
        orm_mode = True


class GetInvites(BaseModel):
    from_id: str


class Message(BaseModel):
    from_id: str
    to_id: str
    message: str
    timestamp: float


class FindUser(BaseModel):
    user_name: str
