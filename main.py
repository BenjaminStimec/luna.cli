import json
import os
import parser
import execute
import color_printing as colp
from color_printing import sys_print
import sys, traceback
import pyparsing

LOGO_TEXT = r"""
  ___     ___ ___ ______  _______    _______ ___     ___
 |   |   |   Y   |   _  \|   _   |  |   _   |   |   |   |
 |.  |   |.  |   |.  |   |.  1   |__|.  1___|.  |   |.  |
 |.  |___|.  |   |.  |   |.  _   |__|.  |___|.  |___|.  |
 |:  1   |:  1   |:  |   |:  |   |  |:  1   |:  1   |:  |
 |::.. . |::.. . |::.|   |::.|:. |  |::.. . |::.. . |::.|
 `-------`-------`--- ---`--- ---'  `-------`-------`---'
 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 """


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

def load_operation(filename):
    with open(filename, 'r') as f:
        operation = json.load(f)
    return operation

def execute_workflow(workflow, kits, vars, alias):
    try:
        parsed_workflow = parser.workflow.parseString(workflow)
        print(parsed_workflow)
    except pyparsing.ParseException as e:
        print(f"Failed to parse workflow at position {e.loc}. Unmatched text: {workflow[e.loc:]}")
        sys.exit(1)
    print("workflow parsed")
    execute.execute_parsed_workflow(parsed_workflow, kits, vars, alias)

def parse_alias(mission):
    alias = mission.get("alias", {})
    for name in alias:
        alias[name] = parser.function_identifier.parseString(alias[name])[0]
    return alias

if __name__ == "__main__":
    #overrides exceptions to print in red color
    sys.excepthook = lambda type, value, tb: sys.stderr.write(colp.color_text(colp.RED, ''.join(traceback.format_exception(type, value, tb))))

    # TODO alias functions - new section in mission files - allow kit.module.function names to be shortened to just 1 word
    sys_print(LOGO_TEXT)
    operation = load_operation("operation.json")
    sys_print("starting operation: " + operation['name'])
    missions = load_all_missions(operation)
    for mission in missions:
        vars = mission.get("vars", {})
        alias = parse_alias(mission)
        workflows = mission["workflows"]
        sys_print("executing mission: " + mission['name'])
        for n, workflow in enumerate(workflows):
            sys_print("executing workflow number: " + str(n+1))
            execute_workflow(workflow, operation['kit_folder'], vars, alias)
