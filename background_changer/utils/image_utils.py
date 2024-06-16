import os
import uuid
from datetime import datetime

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from rembg import new_session, remove
from skimage import io
from torchvision.transforms.functional import normalize

from background_changer.utils.azure_storage import upload_image_to_blob_storage
from background_changer.web.api.change_bg.schema import ChangeBgPositionModelInputDto

from .briarmbg import BriaRMBG


def preprocess_image(im: np.ndarray, model_input_size: list) -> torch.Tensor:
    if len(im.shape) < 3:
        im = im[:, :, np.newaxis]
    # orig_im_size=im.shape[0:2]
    im_tensor = torch.tensor(im, dtype=torch.float32).permute(2, 0, 1)
    im_tensor = F.interpolate(
        torch.unsqueeze(im_tensor, 0),
        size=model_input_size,
        mode="bilinear",
    ).type(torch.uint8)
    image = torch.divide(im_tensor, 255.0)
    image = normalize(image, [0.5, 0.5, 0.5], [1.0, 1.0, 1.0])
    return image


def postprocess_image(result: torch.Tensor, im_size: list) -> np.ndarray:
    result = torch.squeeze(F.interpolate(result, size=im_size, mode="bilinear"), 0)
    ma = torch.max(result)
    mi = torch.min(result)
    result = (result - mi) / (ma - mi)
    im_array = (result * 255).permute(1, 2, 0).cpu().data.numpy().astype(np.uint8)
    im_array = np.squeeze(im_array)
    return im_array


def delete_files(*args):
    for file_path in args:
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Error deleting file {file_path}: {e}")


def resize_pic(
    pic_path: str,
    reference_path: str,
    scale_factor: float = 0.618,
) -> np.ndarray:
    reference = cv2.imread(reference_path)
    pic = cv2.imread(pic_path, cv2.IMREAD_UNCHANGED)

    # Calculate aspect ratio of the reference image
    reference_aspect_ratio = pic.shape[1] / pic.shape[0]

    # Adjust the scale factor if the aspect ratio of the reference image is between 0.8 and 1.2
    if 0.7 <= reference_aspect_ratio <= 1.35:
        scale_factor *= 0.77

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
            output_data = remove(data=output_data, session=rm_session)
            o.write(output_data)


def crop_to_object(image_path, output_path):
    image = Image.open(image_path).convert("RGBA")
    alpha = image.split()[3]
    bbox = alpha.getbbox()
    cropped_image = image.crop(bbox)
    cropped_image.save(output_path, "PNG")


def get_content_type(image_path):
    """Infers content type based on image file extension."""
    extension = image_path.split(".")[-1].lower()
    content_type_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        # Add more extensions as needed
    }
    return content_type_map.get(
        extension,
        "application/octet-stream",
    )  # Default if not found


def change_background_image(
    file_name,
    image_path,
    rm_image_path,
    background_image_path,
    output_image_path,
    position: ChangeBgPositionModelInputDto,
    container_name=None,
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
    if container_name:
        content_type = get_content_type(image_path)
        upload_image_to_blob_storage(
            output_image_path,
            f"{file_name}_chbg.jpg",
            container_name,
            content_type,
        )
    delete_files(
        background_image_path,
        image_path,
        rm_image_path,
        image_path,
        output_image_path,
    )


def remove_background_image(image_path, rm_image_path, crop: bool = True):
    remove_background(image_path, rm_image_path)
    if crop:
        crop_to_object(rm_image_path, rm_image_path)


def remove_background_2(image_path, rm_image_path):
    # net = BriaRMBG()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    net = BriaRMBG.from_pretrained("briaai/RMBG-1.4")
    net.to(device)
    net.eval()

    # prepare input
    model_input_size = [1024, 1024]
    orig_im = io.imread(image_path)
    orig_im_size = orig_im.shape[:2]
    image = preprocess_image(orig_im, model_input_size).to(device)

    # inference
    result = net(image)

    # post process
    result_image = postprocess_image(result[0][0], orig_im_size)

    # save result
    pil_im = Image.fromarray(result_image)
    no_bg_image = Image.new("RGBA", pil_im.size, (0, 0, 0, 0))
    orig_image = Image.open(image_path)
    no_bg_image.paste(orig_image, mask=pil_im)
    no_bg_image.save(rm_image_path)


def remove_background_image_2(image_path, rm_image_path, crop: bool = True):
    remove_background_2(image_path, rm_image_path)
    if crop:
        crop_to_object(rm_image_path, rm_image_path)


def generate_unique_name():
    # Generate a unique identifier using UUID
    unique_id = str(uuid.uuid4().hex)[:8]

    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    return f"image_{timestamp}_{unique_id}"


def change_background_image_2(
    file_name,
    image_path,
    rm_image_path,
    background_image_path,
    output_image_path,
    position: ChangeBgPositionModelInputDto,
    container_name=None,
):
    remove_background_image_2(image_path, rm_image_path)
    crop_to_object(rm_image_path, rm_image_path)
    add_car_to_background(
        rm_image_path,
        background_image_path,
        output_image_path,
        position.height_position,
        position.width_position,
        position.scale_factor,
    )
    if container_name:
        content_type = get_content_type(image_path)
        upload_image_to_blob_storage(
            output_image_path,
            f"{file_name}_chbg.jpg",
            container_name,
            content_type,
        )
    delete_files(
        background_image_path,
        image_path,
        rm_image_path,
        image_path,
        output_image_path,
    )
