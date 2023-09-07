import json
import importlib
from collections import defaultdict


def load_mission(filename):
    with open(filename, 'r') as f:
        mission = json.load(f)
    return mission


def execute_workflow(workflow, vars):
    for step in workflow:
        segments = step.split("=>")
        last_output = None
        for i, segment in enumerate(segments):
            if(segment.startswith("[")):
                continue;
            elif(segment.startswith("await")):
                continue;
            func_str, *args_str = segment.split("(")
            args_str = "".join(args_str)[:-1]  # Remove closing parenthesis and reassemble

            # Split function strings into kit, module, and function
            kit, module, func = func_str.split(".")

            parsed_args = []

            for arg in args_str.split(","):
                if arg.startswith("$"):
                    parsed_args.append(vars.get(arg[1:]))
                elif arg.startswith("%") and last_output != None:
                    parsed_args.append(last_output)
                else:
                    parsed_args.append(arg)

            # Import module and function
            imported_module = importlib.import_module(f"kits.{kit}.{module}")
            func_to_call = getattr(imported_module, func)

            # Call function
            result = func_to_call(*parsed_args)
            last_output = result
            print(result)


if __name__ == "__main__":
    mission = load_mission("missions/SampleMission.json")
    vars = mission.get("vars", {})
    workflow = mission["workflow"]
    execute_workflow(workflow, vars)
