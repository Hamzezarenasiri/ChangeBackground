import io
import shutil

import httpx
from fastapi import APIRouter, BackgroundTasks, UploadFile
from PIL import Image
from pydantic import AnyHttpUrl
from starlette.responses import FileResponse

from background_changer.settings import settings
from background_changer.utils.image_utils import (
    change_background_image,
    change_background_image_2,
    generate_unique_name,
)
from background_changer.web.api.change_bg.schema import (
    BulkChangeBgByLinkModelInputDto,
    BulkChangeBgModelOutputDto,
    ChangeBgByLinkModelInputDto,
    ChangeBgModelOutputDto,
    ChangeBgPositionModelInputDto,
)

router = APIRouter()


async def fetch_and_save_image(url: str, path: str, img_format: str = "JPEG") -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        image_bytes = await response.aread()
        image = Image.open(io.BytesIO(image_bytes))
        # Check if the image is PNG
        if image.format == "PNG":
            # Convert to JPEG
            image = image.convert("RGB")

        image.save(path, format=img_format)


def construct_file_path_and_url(filename: str) -> tuple[str, str]:
    file_path = f"{settings.DEFAULT_MEDIA_PATH}/{filename}"
    file_url = f"{settings.PROJECT_SERVERS[0].get('url')}{file_path}"
    return file_path, file_url


def construct_file_path(filename: str) -> str:
    return f"{settings.DEFAULT_MEDIA_PATH}/{filename}"


async def save_background_image(background_link: AnyHttpUrl, bg_name: str) -> str:
    background_image_path = f"{settings.DEFAULT_MEDIA_PATH}/{bg_name}.jpg"
    await fetch_and_save_image(str(background_link), background_image_path)
    return background_image_path


def change_background_task(
    background_tasks: BackgroundTasks,
    file_name: str,
    image_path: str,
    rm_image_path: str,
    background_image_path: str,
    output_image_path: str,
    position: ChangeBgPositionModelInputDto,
    container_name: str | None,
):
    background_tasks.add_task(
        func=change_background_image,
        file_name=file_name,
        image_path=image_path,
        rm_image_path=rm_image_path,
        background_image_path=background_image_path,
        output_image_path=output_image_path,
        container_name=container_name,
        position=position,
    )


@router.post("/bulk_by_links/", response_model=BulkChangeBgModelOutputDto)
async def bulk_change_backgrounds_by_image_urls(
    background_tasks: BackgroundTasks,
    payload: BulkChangeBgByLinkModelInputDto,
):
    file_links: list[str] = []
    bg_name = f"bg_{generate_unique_name()}"
    background_image_path = await save_background_image(
        payload.background_link,
        bg_name,
    )
    for image_link in payload.image_links:
        file_name = str(generate_unique_name())
        image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_image.jpg"
        await fetch_and_save_image(str(image_link), image_path)
        rm_image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_rmbg.png"
        file_path = construct_file_path(f"{file_name}_chbg.jpg")
        file_url = f"/{payload.container_name}/{file_name}_chbg.jpg"
        print("Public URL to view the image:", file_url)
        file_links.append(file_url)
        change_background_task(
            background_tasks=background_tasks,
            file_name=file_name,
            image_path=image_path,
            rm_image_path=rm_image_path,
            background_image_path=background_image_path,
            output_image_path=file_path,
            container_name=payload.container_name,
            position=payload.position or ChangeBgPositionModelInputDto(),
        )

    return BulkChangeBgModelOutputDto(file_links=file_links)


@router.post("/by_link/", response_model=ChangeBgModelOutputDto)
async def change_background_by_image_urls_t(
    payload: ChangeBgByLinkModelInputDto,
):
    file_name = str(generate_unique_name())
    bg_name = f"bg_{generate_unique_name()}"
    image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_original.jpg"
    background_image_path = await save_background_image(
        payload.background_link,
        bg_name,
    )
    await fetch_and_save_image(str(payload.image_link), image_path)
    rm_image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_rmbg.png"
    file_path = construct_file_path(f"{file_name}_chbg.jpg")
    file_url = f"/{payload.container_name}/{file_name}_chbg.jpg"
    print("Public URL to view the image:", file_url)
    change_background_image(
        file_name=file_name,
        image_path=image_path,
        rm_image_path=rm_image_path,
        background_image_path=background_image_path,
        output_image_path=file_path,
        container_name=payload.container_name,
        position=payload.position or ChangeBgPositionModelInputDto(),
    )
    return ChangeBgModelOutputDto(file_path=file_path, file_link=file_url)


@router.post("/upload/", response_model=ChangeBgModelOutputDto)
def change_background(
    background_tasks: BackgroundTasks,
    image: UploadFile,
    background_image: UploadFile,
) -> ChangeBgModelOutputDto:
    file_name = str(generate_unique_name())
    image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_original.jpg"
    rm_image_path, _ = construct_file_path_and_url(f"{file_name}_rmbg.png")
    background_image_path, _ = construct_file_path_and_url(background_image.filename)
    with open(background_image_path, "wb") as buffer:
        shutil.copyfileobj(background_image.file, buffer)
    with open(image_path, "wb") as buffer2:
        shutil.copyfileobj(image.file, buffer2)
    output_path, image_url = construct_file_path_and_url(f"{file_name}_chbg.jpg")
    change_background_task(
        background_tasks=background_tasks,
        file_name=file_name,
        image_path=image_path,
        rm_image_path=rm_image_path,
        background_image_path=background_image_path,
        output_image_path=output_path,
        # container_name=payload.container_name,
        # position=payload.position or ChangeBgPositionModelInputDto(),
    )
    return ChangeBgModelOutputDto(file_path=output_path, file_link=image_url)


@router.post(
    "/upload_image/",
    response_class=FileResponse,
)
def change_background_and_return_file_t(
    image: UploadFile,
    background_image: UploadFile,
):
    file_name = str(generate_unique_name())
    image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_original.jpg"
    rm_image_path, _ = construct_file_path_and_url(f"{file_name}_rmbg.png")
    background_image_path, _ = construct_file_path_and_url(background_image.filename)
    with open(background_image_path, "wb") as buffer:
        shutil.copyfileobj(background_image.file, buffer)
    with open(image_path, "wb") as buffer2:
        shutil.copyfileobj(image.file, buffer2)
    output_path, _ = construct_file_path_and_url(f"{file_name}_chbg.jpg")
    change_background_image(
        file_name=file_name,
        image_path=image_path,
        rm_image_path=rm_image_path,
        background_image_path=background_image_path,
        output_image_path=output_path,
        position=ChangeBgPositionModelInputDto(),
    )
    return output_path


@router.post(
    "/upload_image_2/",
    response_class=FileResponse,
    tags=["Change Background 2"],
)
def change_background_and_return_file_2(
    image: UploadFile,
    background_image: UploadFile,
):
    file_name = str(generate_unique_name())
    image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_original.jpg"
    rm_image_path, _ = construct_file_path_and_url(f"{file_name}_rmbg.png")
    background_image_path, _ = construct_file_path_and_url(background_image.filename)
    with open(background_image_path, "wb") as buffer:
        shutil.copyfileobj(background_image.file, buffer)
    with open(image_path, "wb") as buffer2:
        shutil.copyfileobj(image.file, buffer2)
    output_path, _ = construct_file_path_and_url(f"{file_name}_chbg.jpg")
    change_background_image_2(
        image_path=image_path,
        rm_image_path=rm_image_path,
        background_image_path=background_image_path,
        output_image_path=output_path,
        position=ChangeBgPositionModelInputDto(),
    )
    return output_path


@router.post(
    "/by_link_image/",
    response_class=FileResponse,
)
async def change_background_by_image_urls_and_return_file(
    payload: ChangeBgByLinkModelInputDto,
):
    file_name = str(generate_unique_name())
    bg_name = f"bg_{generate_unique_name()}"
    image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_original.jpg"
    background_image_path = await save_background_image(
        payload.background_link,
        bg_name,
    )
    await fetch_and_save_image(str(payload.image_link), image_path)
    rm_image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_rmbg.png"
    file_path = construct_file_path(f"{file_name}_chbg.jpg")
    file_url = f"/{payload.container_name}/{file_name}_chbg.jpg"
    print("Public URL to view the image:", file_url)
    change_background_image(
        file_name=file_name,
        image_path=image_path,
        rm_image_path=rm_image_path,
        background_image_path=background_image_path,
        output_image_path=file_path,
        position=payload.position or ChangeBgPositionModelInputDto(),
    )
    return file_path


@router.post(
    "/by_link_image_2/",
    response_class=FileResponse,
    tags=["Change Background 2"],
)
async def change_background_by_image_urls_and_return_file_2(
    payload: ChangeBgByLinkModelInputDto,
):
    file_name = str(generate_unique_name())
    bg_name = f"bg_{generate_unique_name()}"
    image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_original.jpg"
    background_image_path = await save_background_image(
        payload.background_link,
        bg_name,
    )
    await fetch_and_save_image(str(payload.image_link), image_path)
    rm_image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_rmbg.png"
    file_path, _ = construct_file_path_and_url(f"{file_name}_chbg.jpg")
    file_url = f"/{payload.container_name}/{file_name}_chbg.jpg"
    change_background_image_2(
        file_name=file_name,
        image_path=image_path,
        rm_image_path=rm_image_path,
        background_image_path=background_image_path,
        output_image_path=file_path,
        container_name=payload.container_name,
        position=payload.position or ChangeBgPositionModelInputDto(),
    )
    return ChangeBgModelOutputDto(file_path=file_path, file_link=file_url)


@router.post("/bulk_by_links/", response_model=BulkChangeBgModelOutputDto)
async def bulk_change_backgrounds_by_image_urls(
    background_tasks: BackgroundTasks,
    payload: BulkChangeBgByLinkModelInputDto,
):
    file_paths: list[str] = []
    file_links: list[str] = []
    bg_name = f"bg_{generate_unique_name()}"
    background_image_path = await save_background_image(
        payload.background_link,
        bg_name,
    )
    for image_link in payload.image_links:
        file_name = str(generate_unique_name())
        image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_image.jpg"
        await fetch_and_save_image(str(image_link), image_path)
        rm_image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_rmbg.png"
        file_path, file_url = construct_file_path_and_url(f"{file_name}_chbg.jpg")
        file_paths.append(file_path)
        file_links.append(file_url)
        change_background_task(
            background_tasks,
            image_path,
            rm_image_path,
            background_image_path,
            file_path,
            payload.position or ChangeBgPositionModelInputDto(),
        )
    return BulkChangeBgModelOutputDto(file_paths=file_paths, file_links=file_links)


@router.post(
    "/bulk_by_links_2/",
    response_model=BulkChangeBgModelOutputDto,
    tags=["Change Background 2"],
)
async def bulk_change_backgrounds_by_image_urls_2(
    background_tasks: BackgroundTasks,
    payload: BulkChangeBgByLinkModelInputDto,
):
    file_paths: list[str] = []
    file_links: list[str] = []
    bg_name = f"bg_{generate_unique_name()}"
    background_image_path = await save_background_image(
        payload.background_link,
        bg_name,
    )
    for image_link in payload.image_links:
        file_name = str(generate_unique_name())
        image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_image.jpg"
        await fetch_and_save_image(str(image_link), image_path)
        rm_image_path = f"{settings.DEFAULT_MEDIA_PATH}/{file_name}_rmbg.png"
        file_path, file_url = construct_file_path_and_url(f"{file_name}_chbg.jpg")
        file_paths.append(file_path)
        file_links.append(file_url)
        background_tasks.add_task(
            func=change_background_image_2,
            image_path=image_path,
            rm_image_path=rm_image_path,
            background_image_path=background_image_path,
            output_image_path=file_path,
            position=payload.position,
        )
    return BulkChangeBgModelOutputDto(file_paths=file_paths, file_links=file_links)
