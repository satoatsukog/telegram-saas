from pydantic import BaseModel, Field


class SettingsIn(BaseModel):
    tz: str = Field(min_length=1, max_length=64)
    reminder_hour: int | None = Field(default=None, ge=0, le=23)


class DeckIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)


class CardIn(BaseModel):
    front: str = Field(min_length=1, max_length=512)
    back: str = Field(min_length=1, max_length=512)


class PasteIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    text: str = Field(max_length=20000)


class TextIn(BaseModel):
    text: str = Field(max_length=20000)


class GradeIn(BaseModel):
    card_id: int
    grade: str = Field(pattern="^(again|good|easy)$")
