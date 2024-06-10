import torch
from PIL import Image
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.transforms import functional as F


def detect_car_and_remove_bg(input_path, output_path):
    # Load the pre-trained Faster R-CNN model
    model = fasterrcnn_resnet50_fpn(pretrained=True)
    model.eval()

    # Load the image
    image = Image.open(input_path).convert("RGB")
    image_tensor = F.to_tensor(image).unsqueeze(0)

    # Perform inference
    with torch.no_grad():
        prediction = model(image_tensor)

    # Get the highest confidence bounding box
    boxes = prediction[0]["boxes"]
    scores = prediction[0]["scores"]
    high_confidence_idx = scores.argmax()
    print("boxes:", boxes)

    car_box = boxes[high_confidence_idx].numpy().astype(int)
    print("Car scores:", scores)
    print("Car detected at:", car_box)
    max_area = 0
    largest_box = None
    for box in boxes:
        x1, y1, x2, y2 = box
        area = (x2 - x1) * (y2 - y1)
        if area > max_area:
            max_area = area
            largest_box = box.numpy().astype(int)

    print("Largest car detected at:", largest_box)

    # Crop the image to the largest_box
    cropped_image = image.crop(
        (largest_box[0], largest_box[1], largest_box[2], largest_box[3]),
    )
    cropped_image.save(output_path)
    # Since rembg removes the background from the entire image,
    # we first remove the background.
    # bg_removed_image = remove(image.tobytes(), alpha_matting=True)

    # Convert the result back to PIL Image for further processing or saving
    # bg_removed_image_pil = Image.open(io.BytesIO(bg_removed_image))

    # Optionally, you can save or display the image
    # bg_removed_image_pil.save(output_path)
    # bg_removed_image_pil.show()
