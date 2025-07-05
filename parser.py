import pdfplumber
import pandas as pd
from io import StringIO

import google.generativeai as genai
import os

# Your API key config as before...
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

def extract_text_pdfplumber_from_file(file):
    all_text = ""
    # pdfplumber can open from file-like object
    with pdfplumber.open(file) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                all_text += f"\n--- Page {i + 1} ---\n{text}"
    return all_text

def process_pdf_files(uploaded_files):
    all_dfs = []
    successful_files = []

    for uploaded_file in uploaded_files:
        try:
            text = extract_text_pdfplumber_from_file(uploaded_file)
            prompt = f"""
Extract all transactions from the following text. 
Respond ONLY with a valid pipe-separated (|) table with the header: "date|description|amount|category".
- Infer the category from the description. If the description contains 'amazon', use the category 'Amazon', swiggy use Swiggy, Zomato use Zomato.
- Do not include any explanation or extra text.
- Use a + sign for debits (Db) and a - sign for credits (Cr) in the amount.
- Format all dates as YYYY-MM-DD.
- Consolidate similar categories into a single, sensible category name.
- Ensure the amount is a numeric value.

{text}
"""
            response = model.generate_content(prompt)
            llm_output = response.text.strip().replace('`', '')
            df = pd.read_csv(StringIO(llm_output), sep='|', on_bad_lines='skip')
            df.columns = [col.strip() for col in df.columns]
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            df['source_file'] = uploaded_file.name
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            df = df.dropna(subset=['amount'])

            all_dfs.append(df)
            successful_files.append(uploaded_file.name)
        except Exception as e:
            print(f"Error processing {uploaded_file.name}: {e}")

    if not all_dfs:
        return pd.DataFrame(), []

    return pd.concat(all_dfs, ignore_index=True), successful_files