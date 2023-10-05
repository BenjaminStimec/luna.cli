from collections import namedtuple


Variable = namedtuple('Variable', ['name', 'indexing'])
VariableAssignment = namedtuple('VariableAssignment', ['var_name', 'output'])
DataStream = namedtuple('DataStream', ['name'])
Token = namedtuple('Token', ['token', 'indexing'])
LiteralString = namedtuple('LiteralString', ['content'])
DefaultArg = namedtuple('DefaultArg', ['content'])