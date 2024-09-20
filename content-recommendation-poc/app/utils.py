import pandas as pd
import boto3
from io import StringIO
import base64
import json

def load_data(bucket_name: str, file_key: str) -> pd.DataFrame:
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    data = obj['Body'].read().decode('utf-8')
    return pd.read_csv(StringIO(data))

def encode_cursor(id: int, score: float) -> str:
    cursor_data = json.dumps([id, score])
    return base64.b64encode(cursor_data.encode('utf-8')).decode('utf-8')

def decode_cursor(cursor: str) -> tuple:
    cursor_data = base64.b64decode(cursor.encode('utf-8')).decode('utf-8')
    return tuple(json.loads(cursor_data))