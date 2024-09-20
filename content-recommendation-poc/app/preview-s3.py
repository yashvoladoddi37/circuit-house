import pandas as pd
import numpy as np
import boto3
import io
from botocore.exceptions import ClientError

def load_data_from_s3(bucket, key):
    s3 = boto3.client('s3')
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        return pd.read_csv(io.BytesIO(obj['Body'].read()), on_bad_lines='skip', engine='python')
    except ClientError as e:
        print(f"Error loading {key} from S3: {e}")
        raise

def search_id_in_csv(id: str, content_type: str, file_path: str):
    # Load the CSV file from S3 into a DataFrame
    bucket = 'enriched-dataset'
    key = 'filtered_enriched_ch_data_shows.csv'
    df = load_data_from_s3(bucket, key)
    
    result = df[(df['id'] == int(id)) & (df['content_type'] == content_type)]
    result['id'] = result['id'].astype(str)

    return result.reset_index(drop=True)