from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class RemoveBgModelDto(BaseModel):
    """
    Represents the data transfer object (DTO) for the Remove Background Model.

    Attributes:
        id (int): The ID of the model.
        name (str): The name of the model.
        model_config (ConfigDict): The configuration dictionary for the model.

    Examples:
        dto = RemoveBgModelDto(id=1, name="Model 1", model_config={"param1": "value1",
         "param2": "value2"})
    """

    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class RemoveBgPositionModelInputDto(BaseModel):
    """
    Represents the input data transfer object (DTO) for specifying the position
    and scaling of an image on the background.

    Attributes:
        height_position (float, optional): The vertical position of the image on
        the background. Defaults to 0.69.
        width_position (float, optional): The horizontal position of the image on
        the background. Defaults to 0.5.
        scale_factor (float, optional): The scaling factor for the image. Defaults
        to 0.62.

    Examples:
        input_dto = RemoveBgPositionModelInputDto(height_position=0.69,
        width_position=0.5, scale_factor=0.62)
    """

    height_position: float = Field(default=0.69, le=1, ge=0)
    width_position: float = Field(default=0.5, le=1, ge=0)
    scale_factor: float = Field(default=0.62, le=1, ge=0)


class RemoveBgByLinkModelInputDto(BaseModel):
    """
    Represents the input data transfer object (DTO)
    for removing the background of an image by providing links.

    Attributes:
        link (HttpUrl): The URL link to the image.

    Examples:
        input_dto = RemoveBgByLinkModelInputDto(link="https://example.com/car.jpg",
    """

    link: HttpUrl


class BulkRemoveBgByLinkModelInputDto(BaseModel):
    """
    Represents the input data transfer object (DTO)
    for removing the background of an image by providing links.

    Attributes:
        link (HttpUrl): The URL link to the image.

    Examples:
        input_dto = RemoveBgByLinkModelInputDto(link="https://example.com/car.jpg",
    """

    links: list[HttpUrl]


class BulkRemoveBgModelOutputDto(BaseModel):
    """
    Represents the output data transfer object (DTO)
    for the Remove Background API endpoint.

    Attributes:
        file_link (str): The URL link to access the output file.

    Examples:
        output_dto = RemoveBgModelOutputDto(file_link="/output.jpg")
    """

    file_links: list[str]


class RemoveBgModelOutputDto(BaseModel):
    """
    Represents the output data transfer object (DTO)
    for the Remove Background API endpoint.

    Attributes:
        file_path (str): The path to the output file.
        file_link (str): The URL link to access the output file.

    Examples:
        output_dto = RemoveBgModelOutputDto(file_path="output.jpg",
        file_link="/output.jpg")
    """

    file_path: str
    file_link: str
