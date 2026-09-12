from pydantic import BaseModel, ConfigDict, Field

MAX_CARACTERS = 250
MIN_CARACTERS = 3


class CommentCreate(BaseModel):
    content: str = Field(
        default="Legal!", min_length=MIN_CARACTERS, max_length=MAX_CARACTERS
    )
    user_id: int = Field()
    publication_id: int = Field()


class CommentUpdate(BaseModel):
    content: str | None = Field(
        default="Legal!", min_length=MIN_CARACTERS, max_length=MAX_CARACTERS
    )
    user_id: int | None = Field()
    publication_id: int | None = Field(
        default=None, min_length=MIN_CARACTERS, max_length=MAX_CARACTERS
    )


class CommetResponse(BaseModel):
    id: int
    content: str
    user_id: int
    publication_id: int
    model_config = ConfigDict(from_attributes=True)
