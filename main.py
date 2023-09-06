import json
import importlib

def load_and_call_module(module_name, function_name, *args, **kwargs):
    try:
        module = importlib.import_module(module_name)
        func = getattr(module, function_name)
        return func(*args, **kwargs)
    except ImportError:
        return f"Module {module_name} not found."
    except AttributeError:
        return f"Function {function_name} not found in module {module_name}."


if __name__ == "__main__":
    with open("example_workflow.json", "r") as f:
        config = json.load(f)

    task_name = config.get("name")
    print(f"Executing task: {task_name}")

    modules = config.get("modules", {})
    
    for module_name, functions in modules.items():
        for function_name, args in functions.items():
            result = load_and_call_module(module_name, function_name, *args)
            print(f"Result of {module_name}.{function_name}: {result}")
