import requests
import json

def open_file(file_path,encoding='utf-8',*args):
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            content = file.read()
        return content
    except FileNotFoundError:
        raise ValueError(f"File {file_path} does not exists")
    except Exception as e:
        raise ValueError(f"An error has occurred: {e}")

def open_HTML(url,*args):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        raise ValueError(f"An error has occurred: {e}")

def open_json(file_path,*args):
    try:
        return json.loads(open_file(file_path,*args))
    except Exception as e:
        raise ValueError(f"An error has occurred: {e}")

data_stream_parsers = {
    "file" : open_file,
    "html" : open_HTML,
    "json" : open_json
}