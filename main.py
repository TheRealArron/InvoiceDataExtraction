import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from export_to_excel import save_to_excel
from text_cleaning import clean_and_structure_text
from ocr_handler import extract_text_from_image, detect_language, auto_translate  # Import OCR handler functions

# Setup template folder
TEMPLATE_FOLDER = "templates"
os.makedirs(TEMPLATE_FOLDER, exist_ok=True)


def handle_invoice(path, lang_code):
    """Handle the entire invoice processing from OCR to export"""
    extracted_text = extract_text_from_image(path, lang_code)
    lang = detect_language(extracted_text)
    translated_text = auto_translate(extracted_text, lang)

    structured = clean_and_structure_text(translated_text)
    df = pd.DataFrame(structured.items(), columns=["Field", "Value"])

    # Save template for supplier
    if "Supplier" in df["Field"].values:
        supplier = df[df["Field"] == "Supplier"]["Value"].values[0]
        store_template(supplier, translated_text)

    return df, translated_text


def store_template(supplier, text):
    """Store the template of supplier for future use"""
    path = os.path.join(TEMPLATE_FOLDER, f"{supplier}.txt")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def run_gui():
    """Run the GUI for file handling"""
    root = tk.Tk()
    root.title("Smart Invoice OCR")
    root.geometry("800x600")

    lang_options = {
        "English": "eng",
        "Japanese": "jpn",
        "French": "fra",
        "German": "deu",
        "Spanish": "spa",
        "Korean": "kor",
        "Chinese (Simplified)": "chi_sim",
        "Unknown": "unknown"  # Option for auto language detection
    }

    lang_var = tk.StringVar(value="Unknown")

    def browse_file():
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            lang_code = lang_options[lang_var.get()]
            df, full_text = handle_invoice(path, lang_code)
            output.delete(1.0, tk.END)
            output.insert(tk.END, full_text)
            save_to_excel(df)

    def handle_drop(event):
        path = event.data
        if path:
            lang_code = lang_options[lang_var.get()]
            df, full_text = handle_invoice(path, lang_code)
            output.delete(1.0, tk.END)
            output.insert(tk.END, full_text)
            save_to_excel(df)

    tk.Label(root, text="Smart Invoice Processor", font=("Arial", 16)).pack(pady=10)

    lang_dropdown = ttk.Combobox(root, values=list(lang_options.keys()), state="readonly", textvariable=lang_var)
    lang_dropdown.set("Unknown")  # Default language to "Unknown"
    lang_dropdown.pack(pady=5)

    tk.Button(root, text="📁 Browse Invoice", command=browse_file).pack(pady=5)

    output = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20)
    output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    root.mainloop()


if __name__ == "__main__":
    run_gui()
