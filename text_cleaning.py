from transformers import pipeline

#Can use a better model like gpt-4
generator = pipeline("text2text-generation", model="google/flan-t5-large", device=-1)


def clean_and_structure_text(ocr_text):
    prompt = f"""Extract structured invoice data from the text below and return it in JSON format with field names and values.
OCR Text:
{ocr_text}
"""

    print("[INFO] Running the model...")
    result = generator(prompt, max_length=512, do_sample=False)[0]['generated_text']
    print("[INFO] Model returned output.")


    import json
    try:
        structured_data = json.loads(result)
        return structured_data
    except Exception as e:
        print("Warning: Could not parse JSON from model output")
        print("Raw output:", result)
        return {}

if __name__ == "__main__":
    test_text = "Invoice Number: 1234\nSupplier: ABC Corp\nTotal: $500.00"
    print(clean_and_structure_text(test_text))
