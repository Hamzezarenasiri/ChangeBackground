from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, HttpUrl


class ChangeBgModelDto(BaseModel):
    """
    Represents the data transfer object (DTO) for the Change Background Model.

    Attributes:
        id (int): The ID of the model.
        name (str): The name of the model.
        model_config (ConfigDict): The configuration dictionary for the model.

    Examples:
        dto = ChangeBgModelDto(id=1, name="Model 1", model_config={"param1": "value1",
         "param2": "value2"})
    """

    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class ChangeBgPositionModelInputDto(BaseModel):
    """
    Represents the input data transfer object (DTO) for specifying the position and scaling of an image on the background.

    Attributes:
        height_position (float, optional): The vertical position of the  image on the background. Defaults to 0.69.
        width_position (float, optional): The horizontal position of the  image on the background. Defaults to 0.5.
        scale_factor (float, optional): The scaling factor for the  image. Defaults to 0.62.

    Examples:
        input_dto = ChangeBgPositionModelInputDto(height_position=0.69, width_position=0.5, scale_factor=0.62)
    """

    height_position: float = Field(default=0.64, le=1, ge=0)
    width_position: float = Field(default=0.5, le=1, ge=0)
    scale_factor: float = Field(default=0.50, le=1, ge=0)


class ChangeBgByLinkModelInputDto(BaseModel):
    """
    Represents the input data transfer object (DTO)
    for changing the background of an image by providing links.

    Attributes:
        image_link (HttpUrl): The URL link to the  image.
        background_link (AnyHttpUrl): The URL link to the background image.
        position (Change_BgPositionModelInputDTO | None):
        The position of the  image on the background, or None if not specified.

    Examples:
        input_dto = ChangeBgByLinkModelInputDto(image_link="https://example.com/car.jpg",
        background_link="https://example.com/background.jpg",
        position=Change_BgPositionModelInputDTO())
    """

    image_link: HttpUrl
    background_link: AnyHttpUrl
    container_name: str
    position: ChangeBgPositionModelInputDto | None


class BulkChangeBgByLinkModelInputDto(BaseModel):
    """
    Represents the input data transfer object (DTO)
    for changing the background of a  image by providing links.

    Attributes:
        image_link (HttpUrl): The URL link to the  image.
        background_link (AnyHttpUrl): The URL link to the background image.
        position (Change_BgPositionModelInputDTO | None):
        The position of the image on the background, or None if not specified.

    Examples:
        input_dto = ChangeBgByLinkModelInputDto(link="https://example.com/car.jpg",
        background_link="https://example.com/background.jpg",
        position=Change_BgPositionModelInputDTO())
    """

    image_links: list[HttpUrl]
    background_link: AnyHttpUrl
    container_name: str
    position: ChangeBgPositionModelInputDto | None


class BulkChangeBgModelOutputDto(BaseModel):
    """
    Represents the output data transfer object (DTO)
    for the Change Background API endpoint.

    Attributes:
        file_link (AnyHttpUrl): The URL link to access the output file.

    Examples:
        output_dto = ChangeBgModelOutputDto(file_link="https://example.com/output.jpg")
    """

    file_links: list[AnyHttpUrl]


class ChangeBgModelOutputDto(BaseModel):
    """
    Represents the output data transfer object (DTO)
    for the Change Background API endpoint.

    Attributes:
        file_link (AnyHttpUrl): The URL link to access the output file.

    Examples:
        output_dto = ChangeBgModelOutputDto(file_link="https://example.com/output.jpg")
    """

    file_link: AnyHttpUrl
