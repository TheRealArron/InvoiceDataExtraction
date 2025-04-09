from transformers import pipeline
import json
import re
import concurrent.futures

# Load smaller and faster model (flan-t5-small)
print("[DEBUG] Initializing model (flan-t5-small)...")
generator = pipeline("text2text-generation", model="google/flan-t5-small", device=-1)
print("[DEBUG] Model ready.")

def run_with_timeout(prompt, timeout=20):
    """
    Runs the model with a timeout to prevent it from hanging forever.
    """
    print(f"[DEBUG] Starting generation with timeout = {timeout}s")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(generator, prompt, max_length=512, do_sample=False)
        try:
            result = future.result(timeout=timeout)
            print("[DEBUG] Generation completed.")
            return result
        except concurrent.futures.TimeoutError:
            print("[ERROR] Model took too long to respond. Timeout!")
            return None

def clean_model_output(output_text):
    output_text = output_text.strip()
    output_text = re.sub(r"```(json)?", "", output_text).strip()
    return output_text

def clean_and_structure_text(ocr_text):
    prompt = f"""
You are an expert invoice parser. Extract structured invoice data from the OCR text below.
Return the output as **valid JSON** using the field names shown in the example.

Example Input:
Invoice Number: INV12345
Supplier: XYZ Ltd
Total Amount: $1,234.56
Date: 2023-02-15
Due Date: 2023-03-01

Example Output:
{{
  "Invoice Number": "INV12345",
  "Supplier": "XYZ Ltd",
  "Total Amount": "$1,234.56",
  "Date": "2023-02-15",
  "Due Date": "2023-03-01"
}}

OCR Text:
{ocr_text}
"""

    result = run_with_timeout(prompt, timeout=20)
    if not result:
        return {}

    raw_output = result[0]['generated_text']
    cleaned_output = clean_model_output(raw_output)

    try:
        structured_data = json.loads(cleaned_output)
        return structured_data
    except json.JSONDecodeError as e:
        print("[WARNING] Could not parse JSON from model output.")
        print("Raw output:\n", raw_output)
        return {}

# ------------------------
# 🧪 TEST CASE
if __name__ == "__main__":
    test_text = """Invoice Number: 1234
Supplier: ABC Corp
Date: 2023-01-10
Due Date: 2023-01-25
Total: $500.00"""

    print("[INFO] Sending OCR text to model...")
    result = clean_and_structure_text(test_text)
    print("\n🔍 Extracted JSON:")
    print(json.dumps(result, indent=2))
