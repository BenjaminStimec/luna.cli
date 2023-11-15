def translate_complex(value, target_type):
    if target_type == "complex":
        return value
    elif target_type == "str" or target_type == "string":
        return complex_to_string(value)
    else:
        raise ValueError(f"Unsupported target type for translation from complex number: {target_type}")

def complex_to_string(input_complex):
    return str(input_complex)