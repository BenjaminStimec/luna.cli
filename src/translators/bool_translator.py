def translate_bool(value, target_type):
    if target_type == "bool" or target_type == "boolean":
        return value
    elif target_type == "int" or target_type == "integer":
        return boolean_to_integer(value)
    elif target_type == "float":
        return boolean_to_float(value)
    elif target_type == "str" or target_type == "string":
        return boolean_to_string(value)
    else:
        raise ValueError(f"Unsupported target type for translation from boolean: {target_type}")

def boolean_to_integer(input_boolean):
    return int(input_boolean)

def boolean_to_float(input_boolean):
    return float(input_boolean)

def boolean_to_string(input_boolean):
    return str(input_boolean)