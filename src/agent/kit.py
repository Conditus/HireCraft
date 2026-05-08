# Module to prepare tools for an LLM agent

import inspect
import json
from typing import List, Dict, Any, get_type_hints
import re

def python_type_to_json_schema(python_type):
    """Transforms Python types into JSON Schema types"""
    type_mapping = {
        str: 'string',
        int: 'integer',
        float: 'number',
        bool: 'boolean',
        list: 'array',
        dict: 'object',
        List: 'array',
        Dict: 'object',
        'str': 'string',
        'int': 'integer',
        'float': 'number',
        'bool': 'boolean',
        'list': 'array',
        'dict': 'object',
        'List': 'array',
        'Dict': 'object',
    }
    
    if isinstance(python_type, str):
        type_str = python_type
    elif hasattr(python_type, '__name__'):
        type_str = python_type.__name__
    else:
        type_str = str(python_type)
    
    import re
    match = re.match(r'(Optional|Union|List|Dict)\[(.*?)\]', type_str)
    if match:
        base_type = match.group(2).split(',')[0].strip()
        return type_mapping.get(base_type, 'string')
    
    return type_mapping.get(python_type, type_mapping.get(type_str, 'string'))

def get_module_functions(module):
    functions_info = []
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        if not (obj.__module__ == module.__name__ and not name.startswith('_')):
            continue

        doc = inspect.getdoc(obj)

        parsed_doc = parse_function_docstring(doc)

        try:
            sig = inspect.signature(obj)
            type_hints = get_type_hints(obj)
        except (ValueError, TypeError):
            sig = None
            type_hints = {}

        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }

        if sig:
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                    
                param_info = {}
                
                if param_name in parsed_doc["parameters"]["properties"]:
                    param_info["description"] = parsed_doc["parameters"]["properties"][param_name]["description"]
                else:
                    param_info["description"] = f"Parameter {param_name}"

                if param_name in type_hints:
                    param_type = type_hints[param_name]
                    param_info["type"] = python_type_to_json_schema(param_type)
                else:
                    param_info["type"] = "string"

                if param.default is not param.empty:
                    param_info["default"] = param.default
                else:
                    parameters["required"].append(param_name)

                if param_info["type"] == "integer":
                    pass
                elif param_info["type"] == "number":
                    pass
                elif param_info["type"] == "array":
                    pass
                elif param_info["type"] == "string":
                    pass

                parameters["properties"][param_name] = param_info

        functions_info.append({
            "type": "function",
            "name": name,
            "description": parsed_doc["description"],
            "parameters": parameters
        })

    return functions_info

def parse_function_docstring(docstring: str) -> Dict[str, Any]:
    """
    Parses docstring of a function and extracts description + arguments
    
    Args:
        docstring: function documentation
        
    Returns:
        Dict with argumetns and desctiption
    """
    if not docstring:
        return {
            "description": "No description available.",
            "parameters": {"type": "object", "properties": {}}
        }
    
    lines = docstring.strip().split('\n')
    
    description_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith('Args:') or line.startswith('Arguments:'):
            break
        description_lines.append(line)
    
    description = ' '.join(description_lines).strip()
    
    arguments = {}
    in_args_section = False
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('Args:') or line.startswith('Arguments:'):
            in_args_section = True
            continue
        
        if in_args_section:
            if not line:
                continue
            
            match = re.match(r'(\w+):\s*(.+)$', line)
            if match:
                arg_name = match.group(1)
                arg_description = match.group(2).strip()
                arguments[arg_name] = {
                    "description": arg_description,
                }
    
    return {
        "description": description,
        "parameters": {
            "type": "object",
            "properties": arguments
        }
    }

def get_tools():
    """ Init tools as dict: {function_name: function} """
    from src.tools.scraper import item

    tools = {}
    for item in [
        item
        ]:
        tools[item.__name__] = item

    return tools

def get_tools_description():
    """
    Extracts all tools descriptions for an agent
    """
    tools_description = []

    import src.tools.scraper as tool
    module = get_module_functions(tool)
    for item in module:
        tools_description.append(item)
    
    return json.dumps(tools_description, indent=4, ensure_ascii=False)