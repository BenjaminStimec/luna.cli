import json
import os
import workflow_parser
import execute
import pyparsing
import sys
import argparse
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

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
        for path in operation['missions']:
            with open(path, 'r') as f:
                mission = json.load(f)
                missions.append(mission)
    return missions

def load_operation(filename):
    try:
        with open(filename, 'r') as f:
            operation = json.load(f)
        return operation
    except FileNotFoundError:
        raise ValueError(f"File {file_path} does not exists")
    except Exception as e:
        raise ValueError(f"An error has occurred: {e}")


def execute_workflow(workflow, kits, vars, alias):
    try:
        parsed_workflow = workflow_parser.workflow.parseString(workflow)
    except pyparsing.ParseException as e:
        print(f"Failed to parse workflow at position {e.loc}. Unmatched text: {workflow[e.loc:]}")
        sys.exit(1)
    print("workflow parsed")
    execute.execute_parsed_workflow(parsed_workflow, kits, vars, alias)

def parse_alias(mission):
    alias = mission.get("alias", {})
    for name in alias:
        alias[name] = workflow_parser.function_identifier.parseString(alias[name])[0]
    return alias

if __name__ == "__main__":
    print(LOGO_TEXT)

    parser = argparse.ArgumentParser(description='Command line parser for main.py')

    parser.add_argument("-n", "--name", type=str, help="Name of the mission (overwrites operation file argument 'name')")
    parser.add_argument("-o", "--operation-file", type=str, help="Path to the operation file")
    parser.add_argument("-m", "--missions", type=str, nargs="+", help="Paths to mission files")
    parser.add_argument("-k", "--kits", type=str, nargs="+", help="Paths to kit folders")
    parser.add_argument("-mf", "--mission-folder", type=str, help="Path to folder that has mission files (overwrites operation file argument 'mission_folder')")
    parser.add_argument("-kf", "--kit-folder", type=str, help="Path to folder that has kits (overwrites operation file argument 'kit_folder')")

    args = parser.parse_args()

    if(not args.operation_file and args.mission_files):
        operation = dict()
    else:
        operation_file = args.operation_file or "operation.json"
        operation = load_operation(operation_file)
    
    if args.name:
        operation["name"] = args.name
    elif not operation:
        operation["name"] = "Unknown operation "+str(datetime.now())

    if args.kit_folder:
        operation["kit_folder"] = args.kit_folder
    if args.mission_folder
        operation["mission_folder"] = args.mission_folder
        
    if("kits" not in operation):
        operation["kits"] = []

    if("missions" not in operation and args.missions):
        operation["missions"] = args.missions
    elif args.missions:
        operation["missions"] += args.missions

    if("kits" not in operation and args.kits):
        operation["kits"] = args.kits
    elif args.kits:
        operation["kits"] += args.kits
    else:
        operation["kits"] = []

    print(operation)
    print("starting operation: " + operation['name'])
    missions = load_all_missions(operation)

    for mission in missions:
        vars = mission.get("vars", {})
        alias = parse_alias(mission)
        workflows = mission["workflows"]
        print("executing mission: " + mission['name'])
        for n, workflow in enumerate(workflows):
            print("executing workflow number: " + str(n+1))
            execute_workflow(workflow, (operation['kit_folder'],operation["kits"]), vars, alias)