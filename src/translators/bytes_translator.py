def translate_bytes(value, target_type):
    if target_type == "bytes":
        return value
    elif target_type == "str" or target_type == "string":
        return bytes_to_string(value)
    else:
        raise ValueError(f"Unsupported target type for translation from bytes: {target_type}")

def bytes_to_string(input_bytes, encoding='utf-8'):
    return input_bytes.decode(encoding)