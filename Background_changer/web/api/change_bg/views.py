import shutil

import devtools
from fastapi import APIRouter, BackgroundTasks, UploadFile

from background_changer.settings import settings
from background_changer.utils.image_utils import change_background_image
from background_changer.web.api.change_bg.schema import (
    Change_BgModelOutputDTO,
    Change_BgPositionModelInputDTO,
)

router = APIRouter()


@router.post("/upload/", response_model=Change_BgModelOutputDTO)
async def change_background(
    background_tasks: BackgroundTasks,
    car_image: UploadFile,
    background_image: UploadFile,
    # position: Change_BgPositionModelInputDTO = Form(...),
):
    image_path = f"{settings.DEFAULT_MEDIA_PATH}/{car_image.filename}"
    background_image_path = (
        f"{settings.DEFAULT_BACKGROUND_PATH}/{background_image.filename}"
    )
    rm_image_path = f"{settings.DEFAULT_MEDIA_PATH}/rmbg_{car_image.filename}.png"
    out_path = f"{settings.DEFAULT_MEDIA_PATH}/chbg_{car_image.filename}"
    with open(background_image_path, "wb") as buffer:
        shutil.copyfileobj(background_image.file, buffer)
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(car_image.file, buffer)
    position = Change_BgPositionModelInputDTO()
    background_tasks.add_task(
        func=change_background_image,
        image_path=image_path,
        rm_image_path=rm_image_path,
        background_image_path=background_image_path,
        output_image_path=out_path,
        position=position,
    )
    devtools.debug(locals())
    return Change_BgModelOutputDTO(
        file_path=out_path,
        file_link=f"{settings.PROJECT_SERVERS[0].get('url')}/{out_path}",
    )
