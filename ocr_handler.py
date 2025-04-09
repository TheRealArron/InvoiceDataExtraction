import cv2
import pytesseract
import os
from langdetect import detect  # Import langdetect
from deep_translator import GoogleTranslator  # For translation

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def basic_preprocessing(image):
    """Basic preprocessing of image: Grayscale and Thresholding"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh

def advanced_preprocessing(image):
    """Advanced preprocessing of image: Grayscale, Blur, Thresholding, Resizing"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 3)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    resized = cv2.resize(thresh, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
    return resized

def get_confidence_score(image):
    """Calculate the average confidence score of the OCR text"""
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    confs = []

    for conf in data['conf']:
        try:
            conf_int = int(conf)
            if conf_int != -1:
                confs.append(conf_int)
        except ValueError:
            continue

    return sum(confs) / len(confs) if confs else 0

def detect_language(text):
    """Detect language from the extracted text using langdetect"""
    try:
        return detect(text)
    except:
        return 'en'  # Default to English if detection fails

def extract_text_from_image(image_path, lang='eng'):
    """Extract text from an image using Tesseract OCR"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    image = cv2.imread(image_path)
    basic_img = basic_preprocessing(image)
    basic_text = pytesseract.image_to_string(basic_img, config='--oem 3 --psm 6', lang=lang)
    basic_conf = get_confidence_score(basic_img)

    if len(basic_text.strip()) > 30 and basic_conf > 70:
        return basic_text
    else:
        adv_img = advanced_preprocessing(image)
        adv_text = pytesseract.image_to_string(adv_img, config='--oem 3 --psm 6', lang=lang)
        adv_conf = get_confidence_score(adv_img)
        return adv_text

def auto_translate(text, src_lang):
    """Translate the text if the detected language is not English"""
    if src_lang != 'en':
        return GoogleTranslator(source=src_lang, target='en').translate(text)
    return text

# Main function for testing OCR and translation
def main():
    # Define the path to your image
    image_path = "invoice_sample.jpg"  # Replace with the actual image file path

    try:
        # Step 1: Extract text from the image
        extracted_text = extract_text_from_image(image_path)
        print(f"Extracted Text: \n{extracted_text}")

        if extracted_text.strip():
            # Step 2: Detect language of the extracted text
            detected_lang = detect_language(extracted_text)
            print(f"Detected Language: {detected_lang}")

            # Step 3: Optionally translate if the language is not English
            if detected_lang != 'en':
                translated_text = auto_translate(extracted_text, detected_lang)
                print(f"Translated Text: \n{translated_text}")
            else:
                print("No translation needed, text is in English.")
        else:
            print("No text detected in the image.")

    except Exception as e:
        print(f"An error occurred: {e}")

# Entry point to run the test
if __name__ == "__main__":
    main()
