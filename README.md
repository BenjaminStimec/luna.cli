![LunaAI Logo](resources/LunaAI_logo.svg)

Luna.cli is a platform aiming to automate and enhance tasks ranging from everyday chores to enterprise business processes. It relies on Python to perform actions and interact with external system and allows you to use existing python libraries and write new code. To simplify automation it also relies on LLMs to serve as adapters between functions, to fill in missing data from external sources, or to execute complex tasks using data and functions provided by the user.

## Table of Contents

- [Setup Guide](#setup-guide)
- [Operation File](#operation-file)
- [Mission File](#mission-file)
- [Workflow Syntax and Execution](#workflow-syntax-and-execution)
- [Kit Folder](#kit-folder)
- [Kit Instruction Files](#kit-instruction-files),
- [@ Notation](#-notation)
- [CLI](#cli)

## Setup Guide

TODO

## Operation File

Allows you to specify a folder containing mission files or direct paths to mission files that you wish to execute as well as a folder containing kit folders or direct paths to kit folders to bind to those missions during execution
<pre>
sample-oeration.json
{
    "name":"sample-operation",
    "kit_folder":"path/to/kits",
    "kits":["path/to/kitFolder1", "path/to/kitFolder2"],
    "mission_folder":"path/to/missions",
    "missions":["path/to/missionFile1.json", "path/to/missionFile2.json"]
}
</pre>
## Mission File

Serves as the core execution file. Contains a "name" sectiob, a "vars" section for specifying variables as key-value pairs, an "AI" section \(TODO\), an "aliases" section \(TODO\) and "workflows" section which contains workflow strings [Workflow Syntax and Execution](#workflow-syntax-and-execution).
<pre>
sample-mission.json
{
    "name": "sample-mission",
    "alias" : {
        "greet": "sample_kit1.module1.greet"
    },
    "vars": {
        "name_var": "Hello world!"
    },
    "workflows": ["greet($name_var)=>$abc(%1)=>sample_kit2.module2.save_to_file(%all, '1output.txt')"]
}
</pre>
## Workflow Syntax and Execution

TODO

## Kit Folder

Kit folders package together module files which package together python functions. This structure is meant to group functions used to interact with the same system or which perform related actions. Each kit also contains a kit_instructions.json file [Kit Instruction Files](#kit-instruction-files).
<pre>
├── SampleKit/
│   ├── module1.py/
│   ├── module2.py/
│   ├── kit_instruction.json
</pre>
## Kit Instruction Files

They serve as kit documentation for both the user and the LLM using the function and also help during execution:<br/>
The specified modules and functions are the only ones callable in mission files all other files and functions are considered private in the context of luna.cli<br/>
Function descriptions serve for documenting the functionality of the function.<br/>
Function args serve as documentation and for type translation during execution.<br/>
Function output serves for documentation.<br/>
Action informs the user of what is happening at the current step in execution<br/>
<pre>
kit_instructions.json
{
    "sampleModule": {
        "sampleFunction": {
            "description": "Functionality of the function described",
            "args": {
                "name": {
                    "type": "specified primitive type used for translation",
                    "description": "Purpose of the parameter described"
                }
            },
            "output": "Output of the function described",
            "action": "Simple description of the action for use in printing during execution"
        }
    }
}
</pre>
## @ Notation

@ notation is a special syntax used to perform specific pre-defined actions easily.
Currently supported special functions are:
- `@file('path_to_file')` - This function is used to read the contents of a local file. It retrieves and returns the data stored within the specified file.
- `@json('path_to_file')` - This function is used to read and parse a local JSON file. It extracts the structured data from the JSON file, making it accessible for further processing and/or manipulation.
- `@html('url')` - This function is used to retrieve and return the content of a webpage. When provided with the URL of a web page, it fetches the content of that page, which can be useful for web scraping, data extraction, or other web-related tasks.

## CLI
List of arguments:
- `-n`, `--name` - Name of the mission (**overwrites operation file argument 'name'**)
- `-o`, `--operation-file` - Path to the operation file
- `-m`, `--missions` (nargs) - Paths to mission files 
- `-k`, `--kits` (nargs) - Paths to kit folders 
- `-mf`, `--mission-folder` - Path to folder that has mission files (**overwrites operation file argument 'mission_folder'**)
- `-kf`, `--kit-folder` - Path to folder that has kits (**overwrites operation file argument 'kit_folder'**)

If you provide missions or operation-file, default `operation.json` won't be loaded unless specified.