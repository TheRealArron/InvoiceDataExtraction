from rapidfuzz import process
import pandas as pd

valid_codes = {
    "PC001": "Electronics",
    "PC002": "Office Supplies",
    "PC003": "Furniture"
}


def validate_purchase_codes(value):
    result = process.extractOne(value, valid_codes.keys())
    if result:
        best_match, score = result[0], result[1]
        if score > 80:
            return best_match, "Valid", None
        elif score > 50:
            return None, "Invalid", best_match
    return None, "Invalid", None



def suggest_corrections(value):
    if value not in valid_codes:
        result = process.extractOne(value, valid_codes.keys())
        best_match = result[0]
        score = result[1]

        if score > 50:
            return best_match
    return None

#TEST CODE
if __name__ == "__main__":
    sample_data = pd.DataFrame({"Value": ["PC001", "PCO01", "PC004", "PC002"]})

    results = sample_data["Value"].apply(validate_purchase_codes)
    sample_data["Mapped Code"] = results.apply(lambda x: x[0])
    sample_data["Validation"] = results.apply(lambda x: x[1])
    sample_data["Suggested Correction"] = results.apply(lambda x: x[2])

    print(sample_data)

