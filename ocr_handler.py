import cv2
import pytesseract
import numpy as np
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def basic_preprocessing(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh

def advanced_preprocessing(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 3)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    resized = cv2.resize(thresh, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
    return resized

def get_confidence_score(image):
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    confs = [int(conf) for conf in data['conf'] if conf.isdigit()]
    avg_conf = sum(confs) / len(confs) if confs else 0
    return avg_conf

def extract_text_from_image(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    image = cv2.imread(image_path)
    basic_img = basic_preprocessing(image)
    basic_text = pytesseract.image_to_string(basic_img, config='--oem 3 --psm 6')
    basic_conf = get_confidence_score(basic_img)

    if len(basic_text.strip()) > 30 and basic_conf > 70:
        print(f"[INFO] Used basic preprocessing. Confidence: {basic_conf:.2f}")
        return basic_text
    else:
        adv_img = advanced_preprocessing(image)
        adv_text = pytesseract.image_to_string(adv_img, config='--oem 3 --psm 6')
        adv_conf = get_confidence_score(adv_img)
        print(f"[INFO] Used advanced preprocessing. Confidence: {adv_conf:.2f}")
        return adv_text

#visualize detected text boxes
def show_detected_text_boxes(image_path):
    image = cv2.imread(image_path)
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 50:
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imshow("Detected Text Boxes", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    from text_cleaning import clean_and_structure_text
    from data_validation import validate_purchase_codes, suggest_corrections
    from export_to_excel import save_to_excel
    import pandas as pd

    image_path = "invoice_image.jpg"  # Update with your test image

    try:
        extracted_text = extract_text_from_image(image_path)
        structured_data = clean_and_structure_text(extracted_text)

        # Flatten structured JSON to DataFrame
        df = pd.DataFrame(structured_data.items(), columns=["Field", "Value"])

        # Optional: Validate and correct purchase codes
        if "Purchase Code" in df["Field"].values:
            idx = df[df["Field"] == "Purchase Code"].index[0]
            code = df.loc[idx, "Value"]
            validated, status, suggestion = validate_purchase_codes(code)
            df.loc[idx, "Validation"] = status
            df.loc[idx, "Suggested Correction"] = suggestion

        save_to_excel(df)

    except Exception as e:
        print(f"[ERROR] {e}")

