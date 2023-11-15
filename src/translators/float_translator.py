def translate_float(value, target_type):
    if target_type == "float":
        return value
    elif target_type == "int" or target_type == "integer":
        return float_to_integer(value)
    elif target_type == "bool" or target_type == "boolean":
        return float_to_boolean(value)
    elif target_type == "str" or target_type == "string":
        return float_to_string(value)
    else:
        raise ValueError(f"Unsupported target type for translation from float: {target_type}")

def float_to_integer(input_float):
    return int(input_float)

def float_to_boolean(input_float):
    if input_float == 0.0:
        return False
    elif input_float == 1.0:
        return True
    else:
        raise ValueError(f"Cannot convert float '{input_float}' to boolean")

def float_to_string(input_float):
    return str(input_float)