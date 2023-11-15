def translate_int(value, target_type):
    if target_type == "int" or target_type == "integer":
        return value
    elif target_type == "float":
        return integer_to_float(value)
    elif target_type == "bool" or target_type == "boolean":
        return integer_to_boolean(value)
    elif target_type == "str" or target_type == "string":
        return integer_to_string(value)
    else:
        raise ValueError(f"Unsupported target type for translation from integer: {target_type}")

def integer_to_float(input_integer):
    return float(input_integer)

def integer_to_boolean(input_integer):
    if input_integer == 1:
        return True
    elif input_integer == 0:
        return False
    else:
        raise ValueError(f"Cannot convert integer '{input_integer}' to boolean")

def integer_to_string(input_integer):
    return str(input_integer)