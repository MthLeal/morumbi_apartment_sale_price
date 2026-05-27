import pandas as pd
import logging
import unicodedata
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def save_data(data:pd.DataFrame, output_path: str):
    data.to_parquet(output_path, index=False)
    logging.info(f'File saved in {output_path}')

def clean_text(text: str) -> str:
    normalized_text = unicodedata.normalize('NFKD', text)

    text_without_accentuation = normalized_text.encode('ASCII', 'ignore').decode('utf-8')

    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text_without_accentuation)

    return cleaned_text

def normalize_url_text(text: str) -> str:
    text = clean_text(text)

    text = text.lower().replace(' ', '-')

    return text