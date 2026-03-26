import os
import json
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def load_jsonl(folder_name):
    """Load JSONL file from a folder into a pandas DataFrame"""
    folder_path = DATA_DIR / folder_name
    if not folder_path.exists():
        return pd.DataFrame()
    
    jsonl_files = list(folder_path.glob("*.jsonl"))
    if not jsonl_files:
        return pd.DataFrame()
    
    data = []
    for file in jsonl_files:
        with open(file, 'r') as f:
            for line in f:
                data.append(json.loads(line))
    
    return pd.DataFrame(data)

def load_all_data():
    """Load all JSONL files from /app/data into pandas DataFrames"""
    
    import os

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    base_path = os.path.join(BASE_DIR, "../data")
    datasets = {}

    print("Loading data from:", base_path)

    for folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder)

        if not os.path.isdir(folder_path):
            continue

        all_files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.endswith(".jsonl")
        ]

        df_list = []

        for file in all_files:
            try:
                df = pd.read_json(file, lines=True)
                df_list.append(df)
            except Exception as e:
                print(f"Error reading {file}: {e}")

        if df_list:
            combined_df = pd.concat(df_list, ignore_index=True)
        else:
            combined_df = pd.DataFrame()

        datasets[folder] = combined_df

    # Debug print
    print("Data loaded successfully:")
    for name, df in datasets.items():
        print(f"  {name}: {len(df)} records")

    return datasets