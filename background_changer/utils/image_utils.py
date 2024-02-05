import uuid
from datetime import datetime

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

from background_changer.web.api.change_bg.schema import ChangeBgPositionModelInputDto


def resize_pic(
    pic_path: str,
    reference_path: str,
    scale_factor: float = 0.618,
) -> np.ndarray:
    reference = cv2.imread(reference_path)
    pic = cv2.imread(pic_path, cv2.IMREAD_UNCHANGED)

    new_width = int(reference.shape[1] * scale_factor)
    new_height = int((new_width / pic.shape[1]) * pic.shape[0])

    return cv2.resize(pic, (new_width, new_height))


def add_car_to_background(
    car_path: str,
    background_path: str,
    output_path: str,
    height_position: float = 0.69,
    width_position: float = 0.5,
    scale_factor: float = 0.62,
) -> None:
    car_resized = resize_pic(car_path, background_path, scale_factor)

    background = cv2.imread(background_path)
    background_height, background_width, _ = background.shape
    car_height, car_width, _ = car_resized.shape

    x_offset = int(width_position * (background_width - car_width))
    y_offset = int(height_position * (background_height - car_height))

    mask = car_resized[:, :, 3] / 255.0

    for c in range(3):
        background[
            y_offset : y_offset + car_resized.shape[0],
            x_offset : x_offset + car_resized.shape[1],
            c,
        ] = (
            background[
                y_offset : y_offset + car_resized.shape[0],
                x_offset : x_offset + car_resized.shape[1],
                c,
            ]
            * (1 - mask)
            + car_resized[:, :, c] * mask
        )

    cv2.imwrite(output_path, background)


# rm_session = new_session("sam")
rm_session = new_session()


def remove_background(image_path: str, output_path: str) -> None:
    """
    Removes the background from an image and saves the result to the output path.

    Args:
        image_path (str): The path to the input image file.
        output_path (str): The path to save the output image file.

    Returns:
        None

    Examples:
        remove_background("input.jpg", "output.jpg")
    """
    with open(image_path, "rb") as i:
        with open(output_path, "wb") as o:
            input_data = i.read()
            output_data = remove(data=input_data, session=rm_session)
            o.write(output_data)


def crop_to_object(image_path, output_path):
    image = Image.open(image_path).convert("RGBA")
    alpha = image.split()[3]
    bbox = alpha.getbbox()
    cropped_image = image.crop(bbox)
    cropped_image.save(output_path, "PNG")


def change_background_image(
    image_path,
    rm_image_path,
    background_image_path,
    output_image_path,
    position: ChangeBgPositionModelInputDto,
):
    remove_background(image_path, rm_image_path)
    crop_to_object(rm_image_path, rm_image_path)
    add_car_to_background(
        rm_image_path,
        background_image_path,
        output_image_path,
        position.height_position,
        position.width_position,
        position.scale_factor,
    )


def generate_unique_name():
    # Generate a unique identifier using UUID
    unique_id = str(uuid.uuid4().hex)[:8]

    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    return f"image_{timestamp}_{unique_id}"
