from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class Change_BgModelDTO(BaseModel):
    """
    DTO for change_bg models.

    It returned when accessing change_bg models from the API.
    """

    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class Change_BgPositionModelInputDTO(BaseModel):
    """DTO for set size and position of car on background image"""

    height_position: float = Field(default=0.69, le=1, ge=0)
    width_position: float = Field(default=0.5, le=1, ge=0)
    scale_factor: float = Field(default=0.62, le=1, ge=0)


class Change_BgModelOutputDTO(BaseModel):
    """DTO for set size and position of car on background image"""

    file_path: str
    file_link: AnyHttpUrl
