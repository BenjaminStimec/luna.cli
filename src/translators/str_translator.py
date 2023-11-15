import json

def translate_str(value, target_type):
    if target_type == "str" or target_type == "string":
        return value
    elif target_type == "int" or target_type == "integer":
        return string_to_integer(value)
    elif target_type == "float":
        return string_to_float(value)
    elif target_type == "bool" or target_type == "boolean":
        return string_to_boolean(value)
    elif target_type == "dict" or target_type == "dictionary":
        return string_to_dict(value)
    elif target_type == "bytes":
        return string_to_bytes(value)
    elif target_type == "complex":
        return string_to_complex(value)
    else:
        raise ValueError(f"Unsupported target type for translation from string: {target_type}")

def string_to_integer(input_string):
    try:
        return int(input_string)
    except ValueError:
        raise ValueError(f"Cannot convert string '{input_string}' to integer")

def string_to_float(input_string):
    try:
        return float(input_string)
    except ValueError:
        raise ValueError(f"Cannot convert string '{input_string}' to float")

def string_to_boolean(input_string):
    if input_string.lower() in ['true', '1']:
        return True
    elif input_string.lower() in ['false', '0']:
        return False
    else:
        raise ValueError(f"Cannot convert string '{input_string}' to boolean")

def string_to_dict(input_string):
    try:
        return json.loads(input_string)
    except json.JSONDecodeError:
        raise ValueError(f"Cannot convert string '{input_string}' to dictionary")

def string_to_bytes(input_string, encoding='utf-8'):
    return input_string.encode(encoding)

def string_to_complex(input_string):
    try:
        return complex(input_string)
    except ValueError:
        raise ValueError(f"Cannot convert string '{input_string}' to complex number")
