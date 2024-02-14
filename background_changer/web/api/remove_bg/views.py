import io
import shutil

import httpx
from fastapi import APIRouter, BackgroundTasks, UploadFile
from PIL import Image
from pydantic import AnyHttpUrl
from starlette.responses import FileResponse

from background_changer.settings import settings
from background_changer.utils.image_utils import (
    generate_unique_name,
    remove_background_image,
    remove_background_image_2,
)
from background_changer.web.api.remove_bg.schema import (
    BulkRemoveBgByLinkModelInputDto,
    BulkRemoveBgModelOutputDto,
    RemoveBgByLinkModelInputDto,
    RemoveBgModelOutputDto,
)

router = APIRouter()


async def fetch_and_save_image(url: str, path: str, img_format: str = "JPEG") -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        image_bytes = await response.aread()
        image = Image.open(io.BytesIO(image_bytes))
        image.save(path, format=img_format)


def construct_file_path_and_url(filename: str) -> tuple[str, str]:
    file_path = f"{settings.DEFAULT_MEDIA_PATH}/{filename}"
    file_url = f"{settings.PROJECT_SERVERS[0].get('url')}{file_path}"
    return file_path, file_url


@router.post("/upload/", response_model=RemoveBgModelOutputDto)
def remove_background(
    background_tasks: BackgroundTasks,
    image: UploadFile,
) -> RemoveBgModelOutputDto:
    file_name = str(generate_unique_name())
    image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_original.jpg"
    rm_image_path, image_url = construct_file_path_and_url(f"{file_name}_rmbg.png")
    with open(image_path, "wb") as buffer2:
        shutil.copyfileobj(image.file, buffer2)
    background_tasks.add_task(
        func=remove_background_image,
        image_path=image_path,
        rm_image_path=rm_image_path,
    )
    return RemoveBgModelOutputDto(file_path=rm_image_path, file_link=image_url)


@router.post("/by_link/", response_model=RemoveBgModelOutputDto)
async def remove_background_by_image_urls(
    background_tasks: BackgroundTasks,
    payload: RemoveBgByLinkModelInputDto,
):
    file_name = str(generate_unique_name())
    image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_original.jpg"
    await fetch_and_save_image(str(payload.link), image_path)
    rm_image_path, file_url = construct_file_path_and_url(f"{file_name}_rmbg.png")
    background_tasks.add_task(
        func=remove_background_image,
        image_path=image_path,
        rm_image_path=rm_image_path,
    )
    return RemoveBgModelOutputDto(file_path=rm_image_path, file_link=file_url)


@router.post(
    "/upload_image/",
    response_class=FileResponse,
)
def remove_background_and_return_file(
    image: UploadFile,
):
    file_name = str(generate_unique_name())
    image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_original.jpg"
    rm_image_path, _ = construct_file_path_and_url(f"{file_name}_rmbg.png")
    with open(image_path, "wb") as buffer2:
        shutil.copyfileobj(image.file, buffer2)
    remove_background_image(
        image_path=image_path,
        rm_image_path=rm_image_path,
    )
    return rm_image_path


@router.post(
    "/upload_image_2",
    response_class=FileResponse,
    tags=["Remove Background 2"],
)
def remove_background_and_return_file_2(
    image: UploadFile,
):
    file_name = str(generate_unique_name())
    image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_original.jpg"
    rm_image_path, _ = construct_file_path_and_url(f"{file_name}_rmbg.png")
    with open(image_path, "wb") as buffer2:
        shutil.copyfileobj(image.file, buffer2)
    remove_background_image_2(
        image_path=image_path,
        rm_image_path=rm_image_path,
    )
    return rm_image_path


@router.post(
    "/by_link_image/",
    response_class=FileResponse,
)
async def remove_background_by_image_url_and_return_file(
    payload: RemoveBgByLinkModelInputDto,
):
    file_name = str(generate_unique_name())
    image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_original.jpg"
    await fetch_and_save_image(str(payload.link), image_path)
    rm_image_path, _ = construct_file_path_and_url(f"{file_name}_rmbg.png")
    remove_background_image(
        image_path=image_path,
        rm_image_path=rm_image_path,
    )
    return rm_image_path


@router.post(
    "/by_link_image_2/",
    response_class=FileResponse,
    tags=["Remove Background 2"],
)
async def remove_background_by_image_url_and_return_file_2(
    payload: RemoveBgByLinkModelInputDto,
):
    file_name = str(generate_unique_name())
    image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_original.jpg"
    await fetch_and_save_image(str(payload.link), image_path)
    rm_image_path, _ = construct_file_path_and_url(f"{file_name}_rmbg.png")
    remove_background_image_2(
        image_path=image_path,
        rm_image_path=rm_image_path,
    )
    return rm_image_path


@router.post("/bulk_by_links/", response_model=BulkRemoveBgModelOutputDto)
async def bulk_remove_backgrounds_by_image_urls(
    background_tasks: BackgroundTasks,
    payload: BulkRemoveBgByLinkModelInputDto,
):
    file_paths: list[str] = []
    file_links: list[AnyHttpUrl] = []
    for image_link in payload.links:
        file_name = str(generate_unique_name())
        image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_car.jpg"
        await fetch_and_save_image(str(image_link), image_path)
        rm_image_path, file_url = construct_file_path_and_url(f"{file_name}_rmbg.png")
        file_paths.append(rm_image_path)
        file_links.append(file_url)
        background_tasks.add_task(
            func=remove_background_image,
            image_path=image_path,
            rm_image_path=rm_image_path,
        )
    return BulkRemoveBgModelOutputDto(file_paths=file_paths, file_links=file_links)


@router.post(
    "/bulk_by_links_2/",
    response_model=BulkRemoveBgModelOutputDto,
    tags=["Remove Background 2"],
)
async def bulk_remove_backgrounds_by_image_urls_2(
    background_tasks: BackgroundTasks,
    payload: BulkRemoveBgByLinkModelInputDto,
):
    file_paths: list[str] = []
    file_links: list[AnyHttpUrl] = []
    for image_link in payload.links:
        file_name = str(generate_unique_name())
        image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_car.jpg"
        await fetch_and_save_image(str(image_link), image_path)
        rm_image_path, file_url = construct_file_path_and_url(f"{file_name}_rmbg.png")
        file_paths.append(rm_image_path)
        file_links.append(file_url)
        background_tasks.add_task(
            func=remove_background_image_2,
            image_path=image_path,
            rm_image_path=rm_image_path,
        )
    return BulkRemoveBgModelOutputDto(file_paths=file_paths, file_links=file_links)
