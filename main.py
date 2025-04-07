from ocr_handler import extract_text_from_image
from text_cleaning import clean_and_structure_text
from export_to_excel import save_to_excel
from data_validation import validate_purchase_codes, suggest_corrections
import pandas as pd

def main():
    image_path = "invoice_sample.jpg" #Change path to whatevr

    try:
        # Step 1: Extract text fro image
        text = extract_text_from_image(image_path)

        # Step 2: Clean and structre the OCR extracted text
        structured_data = clean_and_structure_text(text)

        # Step 3: Convrt structured data to a DataFrame
        df = pd.DataFrame(structured_data.items(), columns=["Field", "Value"])

        # Step 4: Validate n correct purchase codes if available
        if "Purchase Code" in df["Field"].values:
            idx = df[df["Field"] == "Purchase Code"].index[0]
            code = df.loc[idx, "Value"]
            validated, status, suggestion = validate_purchase_codes(code)
            df.loc[idx, "Validation"] = status
            df.loc[idx, "Suggested Correction"] = suggestion

        # Step 5: Save data to Excel file
        save_to_excel(df)

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
