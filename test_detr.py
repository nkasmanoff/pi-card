from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from PIL import Image
import requests
import time
from transformers import pipeline

import matplotlib.pyplot as plt
from random import choice

url = "https://projects.thecity.nyc/hows-new-york-city-doing/assets/lead-image.jpg"
image = Image.open(requests.get(url, stream=True).raw)

# you can specify the revision tag if you don't want the timm dependency

start = time.time()
processor = DetrImageProcessor.from_pretrained(
    "facebook/detr-resnet-50", revision="no_timm")
model = DetrForObjectDetection.from_pretrained(
    "facebook/detr-resnet-50", revision="no_timm")

end = time.time()
print(f"Time taken to load model: {end - start} seconds")

start = time.time()

inputs = processor(images=image, return_tensors="pt")
outputs = model(**inputs)

end = time.time()

print(f"Time taken to predict: {end - start} seconds")

# convert outputs (bounding boxes and class logits) to COCO API
# let's only keep detections with score > 0.9
target_sizes = torch.tensor([image.size[::-1]])
results = processor.post_process_object_detection(
    outputs, target_sizes=target_sizes, threshold=0.9)[0]

for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
    box = [round(i, 2) for i in box.tolist()]
    print(
        f"Detected {model.config.id2label[label.item()]} with confidence "
        f"{round(score.item(), 3)} at location {box}"
    )


detected_objects_str = "Here's what I saw:\n"

for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
    box = [round(i, 2) for i in box.tolist()]
    detected_objects_str += f"- {model.config.id2label[label.item()]} with confidence {round(score.item(), 3)} at location {box}\n"

print(detected_objects_str)


# save image with bounding boxes


start = time.time()
detector50 = pipeline(model="facebook/detr-resnet-50")
end = time.time()
print(f"Time taken to load model: {end - start} seconds")

start = time.time()
results = detector50(image)
end = time.time()
print(f"Time taken to predict: {end - start} seconds")

COLORS = ["#ff7f7f", "#ff7fbf", "#ff7fff", "#bf7fff",
          "#7f7fff", "#7fbfff", "#7fffff", "#7fffbf",
          "#7fff7f", "#bfff7f", "#ffff7f", "#ffbf7f"]

fdic = {
    "family": "Impact",
    "style": "italic",
    "size": 15,
    "color": "yellow",
    "weight": "bold"
}


def get_figure(in_pil_img, in_results):
    # via https://huggingface.co/spaces/ClassCat/DETR-Object-Detection/blob/main/app.py
    plt.figure(figsize=(16, 10))
    plt.imshow(in_pil_img)
    # pyplot.gcf()
    ax = plt.gca()

    for prediction in in_results:
        selected_color = choice(COLORS)

        x, y = prediction['box']['xmin'], prediction['box']['ymin'],
        w, h = prediction['box']['xmax'] - \
            prediction['box']['xmin'], prediction['box']['ymax'] - \
            prediction['box']['ymin']

        ax.add_patch(plt.Rectangle((x, y), w, h, fill=False,
                     color=selected_color, linewidth=3))
        ax.text(
            x, y, f"{prediction['label']}: {round(prediction['score']*100, 1)}%", fontdict=fdic)

    plt.axis("off")

    return plt.gcf()


figure = get_figure(image, results)
figure.savefig("output.jpg")
