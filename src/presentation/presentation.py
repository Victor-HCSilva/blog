from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class TemplatePreset(str, Enum):
    CLEAN = "clean"
    ACADEMIC = "academic"
    IMMERSIVE = "immersive"
    EDITORIAL = "editorial"


class TypographyFamily(str, Enum):
    SANS = "sans"  # Inter / Geist
    SERIF = "serif"  # Merriweather / Source Serif
    MONO = "mono"  # JetBrains Mono


class TypographySize(str, Enum):
    COMPACT = "compact"
    MEDIUM = "medium"
    EXPANDED = "expanded"


class LayoutWidth(str, Enum):
    NARROW = "narrow"  # 680px (foco extremo)
    STANDARD = "standard"  # 780px (padrão editorial)
    WIDE = "wide"  # 920px (ideal para código/tabelas)


class BackgroundConfig(BaseModel):
    mode: Literal["solid", "gradient", "pattern"] = "solid"
    color: str = Field(pattern=r"^#([A-Fa-f0-9]{6})$", default="#F5F7FA")
    secondary_color: Optional[str] = Field(pattern=r"^#([A-Fa-f0-9]{6})$", default=None)
    accent_color: str = Field(pattern=r"^#([A-Fa-f0-9]{6})$", default="#7C3AED")

    model_config = ConfigDict(extra="forbid")


class PresentationSchema(BaseModel):
    template: TemplatePreset = TemplatePreset.CLEAN
    background: BackgroundConfig = Field(default_factory=BackgroundConfig)
    typography: dict = Field(
        default_factory=lambda: {
            "family": TypographyFamily.SANS,
            "size": TypographySize.MEDIUM,
        }
    )
    layout: dict = Field(
        default_factory=lambda: {
            "width": LayoutWidth.STANDARD,
            "spacing": "comfortable",
        }
    )
