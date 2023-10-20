import requests
import json
from jsonpath_ng import jsonpath, parse
from lxml import etree
import yaml
import re
from bs4 import BeautifulSoup

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
    
def handle_json_replace(data, indexing, value):
    data_to_parse = ""
    isDict = False
    if isinstance(data, str):
        try:
            data_to_parse = json.loads(data)
        except Exception as e:
            raise ValueError(f'Unsuccessfully tried to convert string to json: {str(data)}, Error: {str(e)}')
    elif isinstance(data, dict):
        data_to_parse = data
        isDict = True
    else:
        raise ValueError(f'Unviable data type for use with JSONPath: {str(data)}')
    try:
        jsonpath_expression = parse(indexing)
        print(jsonpath_expression)
    except Exception as e:
        raise ValueError(f'Incorrect JSONPath expression: {str(indexing)}, Error: {str(e)}')
    try:
        result = jsonpath_expression.update(data_to_parse, value)
        if isDict:
            return result
        else:
            return json.dumps(result)
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

def handle_xml_replace(data, indexing, value):
    try:
        tree = etree.fromstring(data)
    except Exception as e:
        raise ValueError(f'Unsuccessfully tried to convert string to XML tree: {str(data)}, Error: {str(e)}')
    
    try:
        matches = tree.xpath(indexing)
        for match in matches:
            if isinstance(match, etree._Element):
                match.text = value
    except Exception as e:
        raise ValueError(f'Failed XPath parsing: {str(data) + indexing}, Error: {str(e)}')

    return etree.tostring(tree, encoding="unicode")

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

def handle_list_replace(data, indexing, value):
    if not isinstance(data, list):
        raise ValueError(f'Expected a list, but got: {type(data).__name__}')
    
    index_exprs = indexing.split(',')
    
    for expr in index_exprs:
        if '-' in expr:
            try:
                start, end = map(int, expr.split('-'))
            except ValueError as e:
                raise ValueError(f'Invalid range expression: {expr}, Error: {str(e)}')
            
            if start >= len(data) or end >= len(data) or start > end:
                raise ValueError(f'Invalid range: {expr}, List length: {len(data)}')

            for i in range(start, end + 1):
                data[i] = value
        else:
            try:
                index = int(expr)
            except ValueError as e:
                raise ValueError(f'Invalid index expression: {expr}, Error: {str(e)}')
            
            if index >= len(data):
                raise ValueError(f'Index out of range: {index}, List length: {len(data)}')

            data[index] = value

    return data

def handle_yaml(data, indexing):
    try:
        data_to_parse = yaml.safe_load(data)
    except Exception as e:
        raise ValueError(f'Unsuccessfully tried to convert string to YAML: {str(data)}, Error: {str(e)}')
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
    
def handle_yaml_replace(data, indexing, value):
    try:
        data_to_parse = yaml.safe_load(data)
    except Exception as e:
        raise ValueError(f'Unsuccessfully tried to convert string to YAML: {str(data)}, Error: {str(e)}')

    try:
        jsonpath_expression = parse(indexing)
    except Exception as e:
        raise ValueError(f'Incorrect JSONPath expression: {str(indexing)}, Error: {str(e)}')
    try:
        jsonpath_expression.update(data_to_parse, value)
        return yaml.dump(data_to_parse)
    except Exception as e:
        raise ValueError(f'Failed JSONPath parsing: {str(data) + str(indexing)}, Error: {str(e)}')

def handle_regex(data, pattern):
    try:
        matches = re.findall(pattern, data)
        return matches
    except Exception as e:
        raise ValueError(f'Failed regex search: {pattern}, Error: {str(e)}')

def handle_regex_replace(data, pattern, replacement):
    try:
        modified_data = re.sub(pattern, replacement, data)
        return modified_data
    except Exception as e:
        raise ValueError(f'Failed regex replace: {pattern} with {replacement}, Error: {str(e)}')

def handle_html(data, selector):
    try:
        soup = BeautifulSoup(data, 'html.parser')
        
        elements = soup.select(selector)
        
        results = [element.get_text() for element in elements]
        
        return results
    except Exception as e:
        raise ValueError(f'Failed HTML search with selector: {selector}, Error: {str(e)}')

def handle_html_replace(data, selector, replacement):
    try:
        soup = BeautifulSoup(data, 'html.parser')
        
        elements = soup.select(selector)
        
        for element in elements:
            element.string = replacement
        
        return str(soup)
    except Exception as e:
        raise ValueError(f'Failed HTML replace with selector: {selector}, Error: {str(e)}')

index_handlers_dict = {
    ("J", "JSON") : (handle_json, handle_json_replace),
    ("X", "XML") : (handle_xml, handle_xml_replace),
    ("L", "LIST") : (handle_list, handle_list_replace),
    ("Y", "YAML") : (handle_yaml, handle_yaml_replace),
    ("R", "REGEX") : (handle_regex, handle_regex_replace),
    ("H", "HTML") : (handle_html, handle_html_replace)
}

flattened_index_handlers_dict = {key: value for keys, value in index_handlers_dict.items() for key in keys}