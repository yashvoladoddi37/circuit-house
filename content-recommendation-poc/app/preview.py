import pandas as pd
import numpy as np


def load_data(file_path):
    return pd.read_csv(file_path)

def search_id_in_csv(search_id: int, content_type: str):
    # Load the CSV file into a DataFrame
    file_path = './datasets/enriched_ch_data_new.csv'
    df = load_data(file_path)
    result = df[(df['id'] == search_id) & (df['content_type'] == content_type)]

    return result.reset_index(drop=True)