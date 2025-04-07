import pandas as pd

def save_to_excel(df, filename="processed_invoice.xlsx"):
    df.to_excel(filename, index=False)
    print(f"Processed invoice data saved to '{filename}'")

if __name__ == "__main__":
    df = pd.DataFrame({"Field": ["Invoice Number", "Supplier", "Total"], "Value": ["1234", "ABC Corp", "$500.00"]})
    save_to_excel(df)
