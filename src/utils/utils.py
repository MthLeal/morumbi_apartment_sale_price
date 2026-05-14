import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def save_data(data:pd.DataFrame, output_path: str):
    data.to_parquet(output_path, index=False)
    logging.info(f'File saved in {output_path}')


