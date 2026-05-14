import pandas as pd
import logging
import re
from pathlib import Path
from utils.utils import save_data


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

input_path_name = Path(__file__).parent.parent.parent / 'data' / 'house_data.parquet'
output_path_name = Path(__file__).parent.parent.parent / 'data' / 'house_data_processed.parquet'

def normalize_numerical_columns(df: pd.DataFrame, int_column_names: list[str], float_column_names: list[str]) -> pd.DataFrame:

    for column in int_column_names:
        df[column] = df[column].apply(lambda x: re.sub(r'\D', '', x))
        df[column] = df[column].astype(int)

    for column in float_column_names:
        df[column] = df[column].apply(
            lambda x: x.replace('R$', '').replace('m²', '').replace('.', '').replace(',', '.')
        )
        df[column] = df[column].astype(float)

    return df

def normalize_address_column(df: pd.DataFrame, column_name: str, new_column_name: str) -> pd.DataFrame:

    df[new_column_name] = df[column_name].apply(lambda x: x.split(',')[1])
    df[column_name] = df[column_name].apply(lambda x: x.split(',')[0])

    return df

def data_transformation() -> pd.DataFrame:

    df = pd.read_parquet(input_path_name)
    df = normalize_numerical_columns(df, ['bedroom_qtd', 'garage'], ['total', 'area'])
    df = normalize_address_column(df, 'address', 'district')

    return df


if __name__ == '__main__':
    processed_df = data_transformation()
    save_data(processed_df, output_path_name)
