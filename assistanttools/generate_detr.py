from transformers import DetrImageProcessor, DetrForObjectDetection
from PIL import Image
import os
from torch import tensor
from config import config

if config["VISION_MODEL"] == 'detr':

    processor = DetrImageProcessor.from_pretrained(
        "facebook/detr-resnet-50", revision="no_timm")
    model = DetrForObjectDetection.from_pretrained(
        "facebook/detr-resnet-50", revision="no_timm")

else:
    processor = None
    model = None


def generate_bounding_box_caption(model, processor):
    os.system(f"espeak 'Taking a picture.'")
    os.system("libcamera-still -o images/detr-image.jpg")
    os.system(f"espeak 'Analyzing the image.'")
    image = Image.open("images/detr-image.jpg")

    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)

    target_sizes = tensor([image.size[::-1]])

    results = processor.post_process_object_detection(
        outputs, target_sizes=target_sizes, threshold=0.9)[0]

    detected_objects_str = "Here's what I saw, and with what pct confidence:\n"

    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        box = [round(i, 2) for i in box.tolist()]
        detected_objects_str += f"- {model.config.id2label[label.item()]} with confidence {round(score.item(), 3)}\n"

    return detected_objects_str
