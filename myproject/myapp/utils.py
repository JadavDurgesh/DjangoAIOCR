import os
import torch
import torchvision.transforms as T
import cv2
import pytesseract
import torchvision
import numpy as np
from PIL import Image

# Path to Tesseract
TESSERACT_PATH = r'/usr/bin/tesseract'#r"C:\Program Files\Tesseract-OCR\tesseract.exe" which tesseract ,  whereis tesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Load Faster R-CNN model
# MODEL_PATH = r"C:\Users\BAPS\Desktop\New folder\myenv\myproject\myapp\model_3.pth"

MODEL_PATH = os.path.dirname(os.path.realpath(__file__))+"/model_3.pth"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

LABEL_MAP = {
    1: "Name",
    2: "CODE",
    3: "Gross Salary",
    4: "I.TAX",
    5: "Profit TAX",
    6: "Treasure voucher No.",
    7: "Treasure voucher Date",
    8: "DDO"
}

model = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights=None)
num_classes = len(LABEL_MAP) + 1
in_features = model.roi_heads.box_predictor.cls_score.in_features
model.roi_heads.box_predictor = torchvision.models.detection.faster_rcnn.FastRCNNPredictor(in_features, num_classes)
#model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.load_state_dict(torch.load(MODEL_PATH, map_location=device), strict=False)
model.to(device)
model.eval()

def extract_text_from_box(image, box):
    x1, y1, x2, y2 = map(int, box)
    cropped_region = image[y1:y2, x1:x2]
    gray = cv2.cvtColor(cropped_region, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    extracted_text = pytesseract.image_to_string(binary, config='--psm 6').strip()
    return extracted_text if extracted_text else None

def detect_text(image_path):
    image = Image.open(image_path).convert("RGB")
    image_cv = cv2.imread(image_path)
    transform = T.Compose([T.ToTensor()])
    image_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        predictions = model(image_tensor)[0]

    extracted_data = {label: [] for label in LABEL_MAP.values()}
    boxes = predictions["boxes"].cpu().numpy()
    labels = predictions["labels"].cpu().numpy()
    scores = predictions["scores"].cpu().numpy()

    sorted_indices = np.argsort(boxes[:, 0])
    boxes, labels, scores = boxes[sorted_indices], labels[sorted_indices], scores[sorted_indices]

    common_values = {"Treasure voucher No.": None, "Treasure voucher Date": None, "DDO": None}

    for i in range(len(boxes)):
        if scores[i] > 0.5:
            box, label_id = boxes[i], labels[i]
            label_name = LABEL_MAP.get(label_id, "Unknown")
            extracted_text = extract_text_from_box(image_cv, box)
            if extracted_text:
                extracted_data[label_name].append(extracted_text)
                if label_name in common_values:
                    common_values[label_name] = extracted_text

    max_rows = max(len(v) for v in extracted_data.values() if isinstance(v, list))

    for key in extracted_data:
        while len(extracted_data[key]) < max_rows:
            extracted_data[key].append(None)

    for key, value in common_values.items():
        if value:
            extracted_data[key] = [value] * max_rows

    # Convert extracted_data dictionary to a list of dictionaries
    structured_data = []
    for i in range(max_rows):
        row = {key: extracted_data[key][i] if i < len(extracted_data[key]) else None for key in extracted_data}
        structured_data.append(row)

    return structured_data
