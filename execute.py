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
def read_kit_instructions(kits,kit):
    try:
        with open(f"{kits}/{kit}/kit_instructions.json","r") as kit_instructions:
            instructions = json.load(kit_instructions)
    except FileNotFoundError:
        raise ValueError(f"kit_instructions.json does not exist in {kits}/{kit}")
    except Exception as e:
        raise ValueError(f"An error has occurred: {e}")
    out = dict()
    for module, data in instructions.items():
        out[module] = set()
        for function in data:
            out[module].add(function)
    return out

def parseArgument(arg, vars, last_output):
    if isinstance(arg, LiteralString) or isinstance(arg, DefaultArg) or isinstance(arg, DefaultIndexString):
        return arg.content
    elif isinstance(arg, Variable):
        if arg.name in vars:
            data = vars[arg.name]
            if arg.indexing != '':
                data = apply_indexing_search(data, arg.indexing.prefix, parseArgument(arg.indexing.content, vars, last_output))
            return data
        else:
            raise ValueError(f"Variable {arg.name} is not defined in the vars dictionary")
    elif isinstance(arg, Token):
        if(last_output != None):
            data = last_output
            if arg.indexing != '':
                data = apply_indexing_search(data, arg.indexing.prefix, parseArgument(arg.indexing.content, vars, last_output))
            return data
        else:
            raise ValueError(f"Last output is not available")
    elif isinstance(arg,DataStream):
        if (arg.name in data_stream_parsers):
            arguments = []
            for i in arg.args:
                arguments.append(parseArgument(i, vars, last_output))
            return data_stream_parsers[arg.name](*arguments)
        else:
            raise ValueError(f"@{arg.name} does not exists in data_stream_parser")
    else:
        raise ValueError(f"Unknown argument type: {type(arg)}")

def execute_parsed_workflow(parsed_workflow, kits, vars, alias):
    last_output = None
    kit_instructions = dict() # cache so that each kit instruction is only parsed once
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
                kit_instructions[kit]=read_kit_instructions(kits,kit) 
            if(module not in kit_instructions[kit]):
                raise ValueError(f"Module '{module}' is either private or does not exist in {kits}/{kit}")
            if(function not in kit_instructions[kit][module]):
                raise ValueError(f"Function '{function}' is either private or does not exist in {kits}/{kit}/{module}")
            
            parsed_args = []
            for arg in action.arguments:
                parsed_args.append(parseArgument(arg, vars, last_output))

            print("imported",kits,kit,module)
            imported_module = importlib.import_module(f"{kits}.{kit}.{module}")
            func_to_call = getattr(imported_module, function)
            last_output = func_to_call(*parsed_args)
        elif isinstance(action, VariableAssignment):
            if(action.indexing != ''):
                vars[action.var_name] = apply_indexing_assign(vars[action.var_name], action.indexing.prefix, parseArgument(action.indexing.content, vars, last_output), parseArgument(action.value, vars, last_output))
            else:
                vars[action.var_name] = parseArgument(action.value, vars, last_output)
            last_output = vars[action.var_name]
        elif isinstance(action, DataStream):
            if (action.name in data_stream_parsers):
                arguments = []
                for i in action.args:
                    arguments.append(parseArgument(i, vars, last_output))
                last_output = data_stream_parsers[action.name](*arguments)
            else:
                raise ValueError(f"@{action.name} does not exists in data_stream_parser")