import json
import importlib
from collections import defaultdict
import os


def load_mission(filename):
    with open(filename, 'r') as f:
        mission = json.load(f)
    return mission

def load_all_missions(operation):
    missions = []
    if('mission_folder' in operation):
        folder=operation['mission_folder']
        for file in os.listdir(folder):
            with open(folder + "/" + file, 'r') as f:
                mission = json.load(f)
                missions.append(mission)
    if('missions' in operation):
        for mission in operation['missions']:
            mission.append(mission)
    return missions

def handle_variable_assignment(variable,value, vars):
    vars.update({variable[1:]:value})

def handle_variable_substitution(arg, vars):
    return vars.get(arg[1:])


def load_operation(filename):
    with open(filename, 'r') as f:
        operation = json.load(f)
    return operation

def process_arguments(args_str, last_output, vars):
    parsed_args = []

    for arg in args_str.split(","):
        if arg.startswith("$"):
            parsed_args.append(handle_variable_substitution(arg, vars))
        elif arg.startswith("%") and last_output != None:
            if(type(last_output) is tuple):
                parsed_args.append(last_output[arg[1:]])
            else:
                parsed_args.append(last_output)
        else:
            parsed_args.append(arg)
    return parsed_args


def execute_workflow(workflow, kit_folder, vars):
    for step in workflow:
        segments = step.split("=>")
        last_output = None
        for i, segment in enumerate(segments):
            if segment.startswith("$") and last_output != None:
                handle_variable_assignment(segment, last_output, vars)
                continue
            if(segment.startswith("[")):
                continue
            elif(segment.startswith("await")):
                continue
            func_str, *args_str = segment.split("(")
            args_str = "".join(args_str)[:-1]  # Remove closing parenthesis and reassemble

            # Split function strings into kit, module, and function
            kit, module, func = func_str.split(".")

            parsed_args = process_arguments(args_str, last_output, vars)
            # Import module and function
            imported_module = importlib.import_module(f"{kit_folder}.{kit}.{module}")
            func_to_call = getattr(imported_module, func)

            # Call function
            result = func_to_call(*parsed_args)
            last_output = result
            print(result)


if __name__ == "__main__":
    operation = load_operation("operation.json")
    print("starting operation: " + operation['name'])
    missions = load_all_missions(operation)
    for mission in missions:
        vars = mission.get("vars", {})
        workflow = mission["workflow"]
        print("executing mission: " + mission['name'])
        execute_workflow(workflow, operation['kit_folder'], vars)
