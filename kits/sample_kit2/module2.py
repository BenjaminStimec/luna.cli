def save_to_file(text, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(text)

def test_at_json(json):
    return json["test"]