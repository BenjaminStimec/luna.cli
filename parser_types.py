from collections import namedtuple


Variable = namedtuple('Variable', ['name'])
VariableAssignment = namedtuple('VariableAssignment', ['var_name', 'output'])
DataStream = namedtuple('DataStream', ['name'])
PreviousOutput = namedtuple('PreviousOutput', ['name'])
LiteralString = namedtuple('LiteralString', ['content'])
DefaultArg = namedtuple('DefaultArg', ['content'])