import cv2
from PIL import Image
from rembg import remove

from background_changer.web.api.change_bg.schema import Change_BgPositionModelInputDTO


def resize_pic_async(pic_path, reference_path, scale_factor=0.618):
    reference = cv2.imread(reference_path)
    pic = cv2.imread(pic_path, cv2.IMREAD_UNCHANGED)

    new_width = int(reference.shape[1] * scale_factor)
    new_height = int((new_width / pic.shape[1]) * pic.shape[0])

    return cv2.resize(pic, (new_width, new_height))


def add_car_to_background_async(
    car_path,
    background_path,
    output_path,
    height_position: float = 0.69,
    width_position: float = 0.5,
    scale_factor: float = 0.62,
):
    car_resized = resize_pic_async(car_path, background_path, scale_factor)

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


def remove_background_async(image_path, output_path):
    with open(image_path, "rb") as i:
        with open(output_path, "wb") as o:
            input_data = i.read()
            output_data = remove(data=input_data)
            o.write(output_data)


def crop_to_object_async(image_path, output_path):
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
    position: Change_BgPositionModelInputDTO,
):
    remove_background_async(image_path, rm_image_path)
    crop_to_object_async(rm_image_path, rm_image_path)
    add_car_to_background_async(
        rm_image_path,
        background_image_path,
        output_image_path,
        position.height_position,
        position.width_position,
        position.scale_factor,
    )
