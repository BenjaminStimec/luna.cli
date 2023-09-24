import importlib
import pyparsing
from parser_types import LiteralString, VariableAssignment, Variable, DataStream, DefaultArg, PreviousOutput

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
                    # TODO: EXPANDED SYNTAX FOR VARIABLE - $name[n] - member of list, $name - entire return, $name[1-5, 7] - ranges, $name['abcd']['efg'][1-9]
                    if arg.name in vars:
                        parsed_args.append(vars[arg.name])
                    else:
                        raise ValueError(f"Variable {arg.name} is not defined in the vars dictionary")
                elif isinstance(arg, PreviousOutput):
                    # TODO: EXPANDED SYNTAX FOR PREVIOUS OUTPUT - %n - member of list, %all - entire return, %[1-5, 7] - ranges, %['abcd']['efg'][1-9]
                    if(last_output != None):
                        parsed_args.append(last_output)
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