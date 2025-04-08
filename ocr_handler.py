import cv2
import pytesseract
import os
from langdetect import detect  # Import langdetect
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Set TCL_LIBRARY path for tkinter
os.environ['TCL_LIBRARY'] = r'C:\Users\regin\AppData\Local\Programs\Python\Python313\tcl\tcl8.6'


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
            # Ensure we only add numeric confidence values and exclude any invalid values (like -1)
            conf_int = int(conf)
            if conf_int != -1:
                confs.append(conf_int)
        except ValueError:
            # If conversion to int fails (non-numeric value), skip it
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
        print(f"[INFO] Used basic preprocessing. Confidence: {basic_conf:.2f}")
        return basic_text
    else:
        adv_img = advanced_preprocessing(image)
        adv_text = pytesseract.image_to_string(adv_img, config='--oem 3 --psm 6', lang=lang)
        adv_conf = get_confidence_score(adv_img)
        print(f"[INFO] Used advanced preprocessing. Confidence: {adv_conf:.2f}")
        return adv_text


# GUI Implementation
def run_gui():
    """Run the GUI for selecting image and performing OCR"""

    def browse_image():
        """Browse for an image file"""
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if path:
            image_path_var.set(path)

    def perform_ocr():
        """Perform OCR on the selected image"""
        path = image_path_var.get()
        lang_code = lang_var.get()

        # If 'Not Known' is selected, auto detect the language
        if lang_code == 'Not Known':
            try:
                # Extract text from the image first without language parameter
                extracted_text = extract_text_from_image(path)

                # Detect language from extracted text
                detected_lang = detect_language(extracted_text)

                # Map detected language to Tesseract OCR supported language
                lang_map = {
                    'en': 'eng',
                    'fr': 'fra',
                    'de': 'deu',
                    'es': 'spa',
                    'ko': 'kor',
                    'zh-cn': 'chi_sim'
                }

                # Select the correct language for OCR
                lang_code = lang_map.get(detected_lang, 'eng')  # Default to English if not in map

                print(f"[INFO] Detected Language: {detected_lang}")
            except Exception as e:
                messagebox.showerror("Error", f"Error in language detection: {str(e)}")
                return

        if not path:
            messagebox.showwarning("No image selected", "Please select an image file.")
            return

        try:
            # Perform OCR with the selected or detected language
            text = extract_text_from_image(path, lang=lang_code)
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, text)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    root = tk.Tk()
    root.title("Invoice OCR Handler")
    root.geometry("700x500")

    image_path_var = tk.StringVar()

    tk.Label(root, text="Select Image:").pack(pady=5)
    tk.Entry(root, textvariable=image_path_var, width=50).pack(pady=5)
    tk.Button(root, text="Browse", command=browse_image).pack(pady=5)

    # Language Dropdown with "Not Known" option for auto-detection
    lang_options = {
        "English": "eng",
        "Japanese": "jpn",
        "French": "fra",
        "German": "deu",
        "Spanish": "spa",
        "Korean": "kor",
        "Chinese (Simplified)": "chi_sim",
        "Not Known": "not_known"  # Option for auto language detection
    }

    lang_var = tk.StringVar(value="eng")

    tk.Label(root, text="Select Language:").pack(pady=5)
    lang_dropdown = ttk.Combobox(root, values=list(lang_options.keys()), state="readonly")
    lang_dropdown.set("English")
    lang_dropdown.pack(pady=5)

    def update_lang_code(event):
        lang_var.set(lang_options[lang_dropdown.get()])

    lang_dropdown.bind("<<ComboboxSelected>>", update_lang_code)

    tk.Button(root, text="Run OCR", command=perform_ocr).pack(pady=10)

    output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15)
    output_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    root.mainloop()


if __name__ == "__main__":
    run_gui()
