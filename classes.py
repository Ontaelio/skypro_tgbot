from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class PresentItem(BaseModel):
    id: int
    title: str
    role: Optional[int]


class GoalItem(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: int
    priority: int
    due_date: Optional[str]
    category: int


class UserStatus(BaseModel):
    id: Optional[int]
    username: Optional[str]
    name: str | None = None
    tg_user: Optional[int]
    board: Optional[PresentItem]
    category: Optional[PresentItem]
    goal: Optional[GoalItem]
    present_boards: Optional[Dict[int, PresentItem]] = {}
    present_cats: Optional[Dict[int, PresentItem]] = {}
    present_goals: Optional[Dict[int, PresentItem]] = {}
    present_comments: Optional[Dict[int, int]] = {}
    default_command: str = '/board'
    session: Any


# telegram message models
class MessageFrom(BaseModel):
    id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


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
