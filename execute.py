import importlib
import json
import pyparsing
from lxml import etree
from jsonpath_ng import jsonpath, parse
from parser_types import LiteralString, VariableAssignment, Variable, DataStream, DefaultArg, Token, FunctionIdentifier, Alias, FunctionCall, Step
import functools
from data_stream import data_stream_parsers

LRU_CACHE_LIMIT = None

def handle_json(data, indexing):
    data_to_parse = ""
    if isinstance(data, str):
        try:
            data_to_parse = json.loads(data)
        except Exception as e:
            raise ValueError(f'Unsuccessfully tried to convert string to json: {str(data)}, Error: {str(e)}')
    elif isinstance(data, dict):
        data_to_parse = data
    else:
        raise ValueError(f'Unviable data type for use with JSONPath: {str(data)}')
    try:
        jsonpath_expression = parse(indexing)
        print(jsonpath_expression)
    except Exception as e:
        raise ValueError(f'Incorrect JSONPath expression: {str(indexing)}, Error: {str(e)}')
    try:
        matches = jsonpath_expression.find(data_to_parse)
        print(matches)
        if len(matches) == 1:
            return matches[0].value
        else:
            return [match.value for match in matches]
    except Exception as e:
        raise ValueError(f'Failed JSONPath parsing: {str(data) + str(indexing)}, Error: {str(e)}')
    

def handle_xml(data, indexing):
    try:
        tree = etree.fromstring(data)
    except Exception as e:
        raise ValueError(f'Unsuccessfully tried to convert string to XML tree: {str(data)}, Error: {str(e)}')
    try:
        matches = tree.xpath(indexing)
        if len(matches) == 1:
            return matches[0].text if isinstance(matches[0], etree._Element) else matches[0]
        else:
            return [match.text if isinstance(match, etree._Element) else match for match in matches]
    except Exception as e:
        raise ValueError(f'Failed XPath parsing: {str(data) + indexing}, Error: {str(e)}')


def handle_list(data, indexing):
    if not isinstance(data, list):
        raise ValueError(f'Expected a list, but got: {type(data).__name__}')
    
    index_exprs = indexing.split(',')
    result = []
    for expr in index_exprs:
        if '-' in expr:
            try:
                start, end = map(int, expr.split('-'))
            except ValueError as e:
                raise ValueError(f'Invalid range expression: {expr}, Error: {str(e)}')
            if start >= len(data) or end >= len(data) or start > end:
                raise ValueError(f'Invalid range: {expr}, List length: {len(data)}')

            result.extend(data[start:end + 1])
        else:
            try:
                index = int(expr)
            except ValueError as e:
                raise ValueError(f'Invalid index expression: {expr}, Error: {str(e)}')
            if index >= len(data):
                raise ValueError(f'Index out of range: {index}, List length: {len(data)}')

            result.append(data[index])
    return result

def apply_indexing(data, indexing):
    expr_type_prefix = indexing[0]
    expr_string = ''.join(indexing[2:-1])
    dispatch_dict = {
        'J': handle_json,
        'X': handle_xml,
        'L': handle_list
    }
    try:
        handler = dispatch_dict[expr_type_prefix]
    except KeyError:
        raise ValueError(f'Unknown expression type prefix: {expr_type_prefix}')
    return handler(data, expr_string)

@functools.lru_cache(maxsize=LRU_CACHE_LIMIT)
def read_kit_instructions(kits,kit):
    try:
        with open(f"{kits}/{kit}/kit_instructions.json","r") as kit_instructions:
            instructions = json.load(kit_instructions)
    except:
        raise ValueError(f"kit_instructions.json does not exist in {kits}/{kit}")
    out = dict()
    for module, data in instructions.items():
        out[module] = set()
        for function in data:
            out[module].add(function)
    return out

def parseArgument(arg, vars, last_output):
    if isinstance(arg, LiteralString) or isinstance(arg, DefaultArg):
        return arg.content
    elif isinstance(arg, Variable):
        if arg.name in vars:
            data = vars[arg.name]
            if arg.indexing != '':
                data = apply_indexing(data, arg.indexing)
            return data
        else:
            raise ValueError(f"Variable {arg.name} is not defined in the vars dictionary")
    elif isinstance(arg, Token):
        if(last_output != None):
            data = last_output
            if arg.indexing != '':
                data = apply_indexing(data, arg.indexing)
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
            if(last_output != None):
                vars[action.var_name] = last_output
            else:
                raise ValueError(f"Last output is not available")