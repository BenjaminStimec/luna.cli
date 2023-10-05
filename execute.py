import importlib
import json
import pyparsing
from lxml import etree
from parser_types import LiteralString, VariableAssignment, Variable, DataStream, DefaultArg, Token

from jsonpath_ng import jsonpath, parse

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
    except Exception as e:
        raise ValueError(f'Incorrect JSONPath expression: {str(indexing)}, Error: {str(e)}')
    try:
        matches = jsonpath_expression.find(data_to_parse)
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

def execute_parsed_workflow(parsed_workflow, kits, vars):
    last_output = None
    for step in parsed_workflow[0]:
        if isinstance(step, pyparsing.results.ParseResults):
            kit, module, function = step.kit, step.module, step.function
            parsed_args = []
            for arg in step.arguments:
                # TODO: add data stream functionality - @ notation (easy syntax for specifying sources of information examples: @file('path_to_file') @html('path_to_url')
                if isinstance(arg, LiteralString) or isinstance(arg, DefaultArg):
                    parsed_args.append(arg.content)
                elif isinstance(arg, Variable):
                    if arg.name in vars:
                        data = vars[arg.name]
                        if arg.indexing is not '':
                            data = apply_indexing(data, arg.indexing)
                        parsed_args.append(data)
                    else:
                        raise ValueError(f"Variable {arg.name} is not defined in the vars dictionary")
                elif isinstance(arg, Token):
                    if(last_output != None):
                        data = last_output
                        if arg.indexing is not '':
                            data = apply_indexing(data, arg.indexing)
                        parsed_args.append(data)
                    else:
                        raise ValueError(f"Last output is not available")
                else:
                    raise ValueError(f"Unknown argument type: {type(arg)}")
            imported_module = importlib.import_module(f"{kits}.{kit}.{module}")
            func_to_call = getattr(imported_module, function)
            last_output = func_to_call(*parsed_args)
        elif isinstance(step, VariableAssignment):
            if(last_output != None):
                vars[step.var_name] = last_output
            else:
                raise ValueError(f"Last output is not available")