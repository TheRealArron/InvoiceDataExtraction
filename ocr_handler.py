import cv2
import pytesseract
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
    confs = [int(conf) for conf in data['conf'] if conf != '']  # Ensure we only process non-empty confidence values
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

#TEST CODE
if __name__ == "__main__":
    image_path = "invoice_sample.jpg"  # Change path as required

    try:
        # Extract text from the image
        extracted_text = extract_text_from_image(image_path)

        # Print the extracted text
        print("[INFO] Extracted OCR Text:")
        print(extracted_text)

    except Exception as e:
        print(f"[ERROR] {e}")
