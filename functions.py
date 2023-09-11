import importlib

def run_function(kit_folder,module_name,function_name,args):
    imported = importlib.import_module(kit_folder+module_name)
    target_function=getattr(imported,function_name)
    out= target_function(*args)   
    print(f"{kit_folder}{module_name}.{function_name}(*{args}) --> {out}" )
    return out        

def execute_workflow(workflow, kit_folder, vars):
    for step in workflow:
        execute=False
        isString=False
        isStringFalseNegative=False
        module_name=""
        isArg=False
        isVar=False
        var=""
        last_output=None
        function_name=""
        args=[]
        indent = 0
        for i in step:
            if(execute and i=='>'):
                isVar=False
                execute=False
                last_output=run_function(kit_folder,module_name,function_name,args)
                args=[]
                function_name=""
                module_name=""
            elif(isVar):
                if(i=='\'' and not isString):
                    isString=True
                    var=''
                elif(isStringFalseNegative):
                    if(i == ','): 
                        args.append(var)
                        var=''
                        isString=False
                    elif(i == ')'):
                        args.append(var)
                        var=''
                        isString=False
                        indent-=1
                        if(indent == 0):
                            isVar=False
                    else:
                        var+='\''+i
                    isStringFalseNegative=False
                elif(isString):
                    if(i=='\''):
                        isStringFalseNegative=True
                    else:
                        var+=i

                else:
                    if(i=='('):
                        indent+=1
                    elif(i=='$'):
                        pass
                    elif(i=='%'):
                        isArg=True
                    elif(i  == ',' or i == ')'):
                        var+=i
                    else:
                        if(isArg):
                            if(type(last_output) is tuple):
                                args.append(last_output[int(var)])
                            else:
                                args.append(last_output)
                            isArg = False
                        else:
                            variable=vars.get(var)
                            if(variable):
                                args.append(variable)
                        var=""
                    if(i==')'):
                        indent-=1
                        if(indent == 0):
                            isVar=False
            else:
                if(i=='('):
                    indent+=1
                    isVar=True
                elif(i=='='):
                    execute=True
                elif(i=='.'):
                    module_name+=f".{function_name}"
                    function_name=""
                else:
                    function_name+=i
        run_function(kit_folder,module_name,function_name,args)