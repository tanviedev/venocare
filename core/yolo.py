from ultralytics import YOLO
import os
from PIL import Image

model_path = os.path.join("model", "best.pt")
model = YOLO(model_path)


def predict(image_path):
    from ultralytics import YOLO
    import os
    import cv2
    from PIL import Image
    import numpy as np

    model = YOLO("model/best.pt")
    results = model(image_path)

    if not results or not results[0].boxes:
        return None, None, None, None

    labels = []
    for box in results[0].boxes.data:
        cls_id = int(box[-1])
        label = model.names[cls_id]
        labels.append(label)

    # Save annotated image
    annotated_image = results[0].plot()  # returns a numpy array
    result_image_path = image_path.replace("media", "media/results")
    os.makedirs(os.path.dirname(result_image_path), exist_ok=True)
    cv2.imwrite(result_image_path, annotated_image)

    # Determine status
    if "infected" in labels:
        status = "Infected"
    elif "normal" in labels:
        status = "Normal"
    else:
        status = "Unknown"

    return results[0], result_image_path.replace('\\', '/'), status, labels
