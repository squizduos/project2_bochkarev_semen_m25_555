import json
import os


def load_metadata(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_table_data(table_name):
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    filepath = os.path.join(data_dir, f'{table_name}.json')
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    filepath = os.path.join(data_dir, f'{table_name}.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

