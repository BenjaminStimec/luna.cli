import importlib
import json
import pyparsing
from parser_types import LiteralString, VariableAssignment, Variable, DataStream, DefaultArg, Token, FunctionIdentifier, Alias, FunctionCall, DefaultIndexString
import functools
from data_stream import data_stream_parsers
from index_handelers import flattened_index_handlers_dict

LRU_CACHE_LIMIT = None

def apply_indexing_search(data, prefix, content):
    try:
        handler = flattened_index_handlers_dict[prefix.upper()][0]
    except KeyError:
        raise ValueError(f'Unknown expression type prefix: {prefix}')
    
    return handler(data, content)

def apply_indexing_assign(data, prefix, content, value):
    try:
        handler = flattened_index_handlers_dict[prefix.upper()][1]
    except KeyError:
        raise ValueError(f'Unknown expression type prefix: {prefix}')
    
    return handler(data, content, value)

@functools.lru_cache(maxsize=LRU_CACHE_LIMIT)
def read_kit_instructions(kit_path):
    try:
        with open(f"{kit_path}/kit_instructions.json", "r") as kit_instructions:
            instructions = json.load(kit_instructions)
    except FileNotFoundError:
        raise ValueError(f"kit_instructions.json does not exist in {kit_path}")
    except Exception as e:
        raise ValueError(f"An error has occurred: {e}")

    out = dict()
    for module, functions in instructions.items():
        out[module] = {}
        for function_name, function_data in functions.items():
            out[module][function_name] = {
                'description': function_data.get('description'),  # Add this line
                'args': function_data.get('args', {}),
                'output': function_data.get('output'),
                'action': function_data.get('action')
            }
    return out


def parse_argument(arg, vars, last_output):
    if isinstance(arg, LiteralString) or isinstance(arg, DefaultArg) or isinstance(arg, DefaultIndexString):
        return arg.content
    elif isinstance(arg, Variable):
        if arg.name in vars:
            data = vars[arg.name]
            if arg.indexing != '':
                data = apply_indexing_search(data, arg.indexing.prefix, parse_argument(arg.indexing.content, vars, last_output))
            return data
        else:
            raise ValueError(f"Variable {arg.name} is not defined in the vars dictionary")
    elif isinstance(arg, Token):
        if(last_output != None):
            data = last_output
            if arg.indexing != '':
                data = apply_indexing_search(data, arg.indexing.prefix, parse_argument(arg.indexing.content, vars, last_output))
            return data
        else:
            raise ValueError(f"Last output is not available")
    elif isinstance(arg,DataStream):
        if (arg.name in data_stream_parsers):
            arguments = []
            for i in arg.args:
                arguments.append(parse_argument(i, vars, last_output))
            return data_stream_parsers[arg.name](*arguments)
        else:
            raise ValueError(f"@{arg.name} does not exists in data_stream_parser")
    else:
        raise ValueError(f"Unknown argument type: {type(arg)}")
    
def translate(input_data, target_type):
    input_type = type(input_data).__name__
    translator_module = f"translators.{input_type}_translator"

    # if types match return as is
    if input_type == target_type:
        return input_data
    try:
        translator = importlib.import_module(translator_module)
    except ImportError:
        raise ValueError(f"No translator available for type {input_type}")
    
    translate_func = getattr(translator, f"translate_{input_type}", None)
    if translate_func is None:
        raise ValueError(f"Translator for {input_type} does not support conversion to {target_type}")

    return translate_func(input_data, target_type)

def function_call(kit, module, function, parsed_args):
    imported_module = importlib.import_module(f"{kit}.{module}")
    func_to_call = getattr(imported_module, function)
    last_output = func_to_call(*parsed_args)
    return last_output

def execute_parsed_workflow(parsed_workflow, kits, vars, alias):
    last_output = None
    kit_instructions = dict() # cache so that each kit instruction is only parsed once
    kits_paths = dict()
    for i in kits[1]:
        temp = i.split("/")
        kits_paths[temp[-1]] = i
    for action in parsed_workflow:
        if isinstance(action, FunctionCall):
            if isinstance(action.identifier, Alias):
                if action.identifier.name in alias:
                    temp = alias[action.identifier.name]
                    kit, module, function = temp.kit, temp.module, temp.function
                else:
                    raise ValueError(f"Alias is not available")
            else: 
                kit, module, function = action.identifier.kit, action.identifier.module, action.identifier.function
            
            if(kit not in kit_instructions):
                if kit in kits_paths:
                    kit_path = kits_paths[kit]  
                elif kits[0]:
                    kit_path = f"{kits[0]}/{kit}"
                else:
                    raise ValueError(f"Kit {kit} has not been found")
                kit_instructions[kit]=read_kit_instructions(kit_path)
                kit_path = kit_path.replace("/",".")
            if(module not in kit_instructions[kit]):
                raise ValueError(f"Module '{module}' is either private or does not exist in {kits}/{kit}")
            if(function not in kit_instructions[kit][module]):
                raise ValueError(f"Function '{function}' is either private or does not exist in {kits}/{kit}/{module}")

            func_args_spec = kit_instructions[kit][module][function].get('args', {})
            parsed_args = []
            for arg_name, arg in zip(func_args_spec, action.arguments):
                target_type = func_args_spec[arg_name].get('type')
                translated_arg = translate(parse_argument(arg, vars, last_output), target_type)
                parsed_args.append(translated_arg)

            output = function_call(kit_path, module, function, parsed_args)
            if output:
                last_output = output
            
        elif isinstance(action, VariableAssignment):
            if(action.indexing != ''):
                vars[action.var_name] = apply_indexing_assign(vars[action.var_name], action.indexing.prefix, parse_argument(action.indexing.content, vars, last_output), parse_argument(action.value, vars, last_output))
            else:
                vars[action.var_name] = parse_argument(action.value, vars, last_output)
            last_output = vars[action.var_name]
        elif isinstance(action, DataStream):
            if (action.name in data_stream_parsers):
                arguments = []
                for i in action.args:
                    arguments.append(parse_argument(i, vars, last_output))
                last_output = data_stream_parsers[action.name](*arguments)
            else:
                raise ValueError(f"@{action.name} does not exists in data_stream_parser")