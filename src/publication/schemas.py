from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from presentation.presentation import (
    BackgroundConfig,
    LayoutWidth,
    TemplatePreset,
    TypographyFamily,
    TypographySize,
)


class InlineStyles(BaseModel):
    bold: bool = False
    italic: bool = False
    code: bool = False


class InlineContent(BaseModel):
    type: Literal["text", "link"] = "text"
    text: str = Field(min_length=1)
    href: HttpUrl | None = None
    styles: InlineStyles = Field(default_factory=InlineStyles)


class HeadingProps(BaseModel):
    level: int = Field(default=2, ge=1, le=6)


class CodeBlockProps(BaseModel):
    language: str | None = Field(default=None, min_length=1, max_length=32)


class ListProps(BaseModel):
    ordered: bool = False


class DocumentBlock(BaseModel):
    type: Literal["paragraph", "heading", "codeBlock", "quote", "list"]
    props: HeadingProps | CodeBlockProps | ListProps | None = None
    content: list[InlineContent] = Field(default_factory=list)
    items: list[list[InlineContent]] = Field(default_factory=list)


class DocumentSchema(BaseModel):
    blocks: list[DocumentBlock] = Field(default_factory=list)


class TypographyConfig(BaseModel):
    family: TypographyFamily = TypographyFamily.SANS
    size: TypographySize = TypographySize.MEDIUM

    model_config = ConfigDict(extra="forbid")


class LayoutConfig(BaseModel):
    width: LayoutWidth = LayoutWidth.STANDARD
    spacing: Literal["comfortable", "compact"] = "comfortable"

    model_config = ConfigDict(extra="forbid")


class PublicationPresentation(BaseModel):
    """Author design intentions; arbitrary CSS values are intentionally forbidden."""

    template: TemplatePreset = TemplatePreset.CLEAN
    background: BackgroundConfig = Field(default_factory=BackgroundConfig)
    typography: TypographyConfig = Field(default_factory=TypographyConfig)
    layout: LayoutConfig = Field(default_factory=LayoutConfig)

    model_config = ConfigDict(extra="forbid")


class PublicationBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(
        min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    )
    document: DocumentSchema
    presentation: PublicationPresentation

    model_config = ConfigDict(extra="forbid")


class PublicationCreate(PublicationBase):
    user_id: int | None = None


class PublicationUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    document: DocumentSchema
    presentation: PublicationPresentation

    model_config = ConfigDict(extra="forbid")


class PublicationResponse(PublicationBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True, extra="forbid")
