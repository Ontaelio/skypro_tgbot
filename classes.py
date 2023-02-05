from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class PresentItem(BaseModel):
    id: int
    title: str


class UserStatus(BaseModel):
    username: str
    name: str | None = None
    board: Optional[PresentItem]
    category: int | None = None
    goal: int | None = None
    present_boards: Optional[Dict[int, PresentItem]]
    present_cats: Optional[Dict[int, PresentItem]]
    present_goals: Optional[Dict[int, PresentItem]]
    session: Any


# telegram message models
class MessageFrom(BaseModel):
    id: int
    username: str | None = None


class Chat(BaseModel):
    id: int
    username: str | None = None


class Message(BaseModel):
    message_id: int
    from_: MessageFrom = Field(..., alias='from')
    chat: Chat
    text: str | None = None

    class Config:
        allow_population_by_field_name = True


class UpdateObj(BaseModel):
    def __init__(self, **data):
        super().__init__(
            message=data.pop("message", None) or data.pop("edited_message", None),
            **data,
        )

    update_id: int
    message: Message


class GetUpdatesResponse(BaseModel):
    ok: bool
    result: list[UpdateObj] = []


class SendMessageResponse(BaseModel):
    ok: bool
    result: Message
