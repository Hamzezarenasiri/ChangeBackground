import io
import shutil

import httpx
from fastapi import APIRouter, BackgroundTasks, UploadFile
from PIL import Image

from background_changer.settings import settings
from background_changer.utils.image_utils import (
    change_background_image,
    generate_unique_name,
)
from background_changer.web.api.change_bg.schema import (
    ChangeBgByLinkModelInputDto,
    ChangeBgModelOutputDto,
    ChangeBgPositionModelInputDto,
)

router = APIRouter()


@router.post("/by_links/", response_model=ChangeBgModelOutputDto)
async def change_background_by_image_urls(
    background_tasks: BackgroundTasks,
    payload: ChangeBgByLinkModelInputDto,
):
    async with httpx.AsyncClient() as client:
        response = await client.get(str(payload.car_link))
        response.raise_for_status()
        image_bytes = await response.aread()
        image = Image.open(io.BytesIO(image_bytes))
        car_path = f"{settings.DEFAULT_MEDIA_PATH}/car_{generate_unique_name()}.jpg"
        image.save(car_path, format="JPEG")
        back_response = await client.get(str(payload.background_link))
        back_response.raise_for_status()
        back_image_bytes = await back_response.aread()
        back_image = Image.open(io.BytesIO(back_image_bytes))
        background_image_path = (
            f"{settings.DEFAULT_MEDIA_PATH}/bg_{generate_unique_name()}.jpg"
        )
        back_image.save(background_image_path, format="JPEG")

    rm_image_path = f"{settings.DEFAULT_MEDIA_PATH}/rmbg_{generate_unique_name()}.png"
    out_path = f"{settings.DEFAULT_MEDIA_PATH}/chbg_{generate_unique_name()}.jpg"
    background_tasks.add_task(
        func=change_background_image,
        image_path=car_path,
        rm_image_path=rm_image_path,
        background_image_path=background_image_path,
        output_image_path=out_path,
        position=payload.position or ChangeBgPositionModelInputDto(),
    )
    return ChangeBgModelOutputDto(
        file_path=out_path,
        file_link=f"{settings.PROJECT_SERVERS[0].get('url')}{out_path}",
    )


@router.post("/upload/", response_model=ChangeBgModelOutputDto)
def change_background(
    background_tasks: BackgroundTasks,
    car_image: UploadFile,
    background_image: UploadFile,
) -> ChangeBgModelOutputDto:
    """
    Changes the background of a car image using the provided background image.

    Args:
        background_tasks (BackgroundTasks): The background tasks manager.
        car_image (UploadFile): The car image file to change the background of.
        background_image (UploadFile): The background image file to use.

    Return:
        ChangeBgModelOutputDto: The output data transfer object (DTO) containing
        the path and link to the changed background image.

    Examples:
        output_dto = change_background(background_tasks, car_image, background_image)
    """
    image_path = f"{settings.DEFAULT_MEDIA_PATH}/{car_image.filename}"
    background_image_path = (
        f"{settings.DEFAULT_BACKGROUND_PATH}/{background_image.filename}"
    )
    with open(background_image_path, "wb") as buffer:
        shutil.copyfileobj(background_image.file, buffer)
    with open(image_path, "wb") as buffer2:
        shutil.copyfileobj(car_image.file, buffer2)
    background_tasks.add_task(
        func=change_background_image,
        image_path=image_path,
        rm_image_path=f"{settings.DEFAULT_MEDIA_PATH}/rmbg_{car_image.filename}.png",
        background_image_path=background_image_path,
        output_image_path=f"{settings.DEFAULT_MEDIA_PATH}/chbg_{car_image.filename}",
        position=ChangeBgPositionModelInputDto(),
    )
    return ChangeBgModelOutputDto(
        file_path=f"{settings.DEFAULT_MEDIA_PATH}/chbg_{car_image.filename}",
        file_link=f"{settings.PROJECT_SERVERS[0].get('url')}{settings.DEFAULT_MEDIA_PATH}/chbg_{car_image.filename}",
    )
