import json
import os
import parser
import execute
import color_printing as colp
import sys, traceback

LOGO_TEXT = """
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

def execute_workflow(workflow, kits, vars):
    parsed_workflow = parser.workflow.parseString(workflow)
    execute.execute_parsed_workflow(parsed_workflow, kits, vars)

if __name__ == "__main__":
    #overrides exceptions to print in red color
    sys.excepthook = lambda type, value, tb: sys.stderr.write(colp.color_text(colp.RED, ''.join(traceback.format_exception(type, value, tb))))

    # TODO alias functions - new section in mission files - allow kit.module.function names to be shortened to just 1 word
    colp.sys_print(LOGO_TEXT)
    operation = load_operation("operation.json")
    colp.sys_print("starting operation: " + operation['name'])
    missions = load_all_missions(operation)
    for mission in missions:
        vars = mission.get("vars", {})
        workflows = mission["workflows"]
        colp.sys_print("executing mission: " + mission['name'])
        for n, workflow in enumerate(workflows):
            colp.sys_print("executing workflow number: " + str(n+1))
            execute_workflow(workflow, operation['kit_folder'], vars)
