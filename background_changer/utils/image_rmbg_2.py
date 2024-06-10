import torch
from PIL import Image, ImageOps
from transformers import AutoFeatureExtractor, AutoModelForImageSegmentation


def remove_background_2b(input_path, output_path):
    # Initialize the feature extractor and model
    feature_extractor = AutoFeatureExtractor.from_pretrained("briaai/RMBG-1.4")
    model = AutoModelForImageSegmentation.from_pretrained("briaai/RMBG-1.4")

    # Load the image
    image = Image.open(input_path).convert("RGB")

    # Preprocess the image
    inputs = feature_extractor(images=image, return_tensors="pt")

    # Predict the mask
    outputs = model(**inputs)
    output = outputs.logits[0]

    # Apply softmax to convert logits to probabilities
    probs = torch.nn.functional.softmax(output, dim=0)[1]

    # Threshold the probabilities to create a binary mask
    mask = probs > 0.5

    # Create a binary mask for PIL (255 for foreground, 0 for background)
    mask = mask.mul(255).byte().cpu().numpy()
    mask = Image.fromarray(mask).resize(image.size, resample=Image.BILINEAR)
    mask = ImageOps.invert(
        mask,
    )  # Invert mask (depending on your model's convention, you might not need this line)

    # Prepare output image: create a blank image with a transparent background
    output_image = Image.new("RGBA", image.size)
    output_image.paste(image, (0, 0), mask)

    # Save the output image
    output_image.save(output_path)
