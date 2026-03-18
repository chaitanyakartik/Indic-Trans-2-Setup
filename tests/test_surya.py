from PIL import Image
from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor
import json

# ---- Load image ----
image = Image.open(
    '/home/chaitanya/translation-model/Indic-Trans-2-Setup/test_image_kn_2.png'
)

# ---- Init predictors ----
foundation_predictor = FoundationPredictor()
recognition_predictor = RecognitionPredictor(foundation_predictor)
detection_predictor = DetectionPredictor()

# ---- Run OCR ----
predictions = recognition_predictor([image], det_predictor=detection_predictor)

print("\n===== STRUCTURE INSPECTION =====\n")

for page_idx, page in enumerate(predictions):
    print(f"\n📄 Page {page_idx}")

    # Try printing available attributes
    print("\nPage attributes:")
    print(dir(page))

    for line_idx, line in enumerate(page.text_lines):
        print("\n----------------------------")
        print(f"🧾 Line {line_idx}")

        # Raw object attributes
        print("Line attributes:")
        print(dir(line))

        # ---- Extract text ----
        try:
            line_text = "".join([char.text for char in line.chars])
        except Exception:
            line_text = getattr(line, "text", "UNKNOWN")

        print("Text:", line_text)

        # ---- Bounding Box ----
        bbox = getattr(line, "bbox", None)
        print("BBox:", bbox)

        # ---- Confidence (if exists) ----
        conf = getattr(line, "confidence", None)
        print("Confidence:", conf)

        # ---- Character-level info ----
        if hasattr(line, "chars"):
            print("\nCharacters:")
            for c in line.chars:
                char_bbox = getattr(c, "bbox", None)
                char_conf = getattr(c, "confidence", None)
                print({
                    "char": c.text,
                    "bbox": char_bbox,
                    "conf": char_conf
                })