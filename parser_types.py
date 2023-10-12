from collections import namedtuple


Variable = namedtuple('Variable', ['name', 'indexing'])
VariableAssignment = namedtuple('VariableAssignment', ['var_name', 'output'])
DataStream = namedtuple('DataStream', ['name', 'args'])
Token = namedtuple('Token', ['token', 'indexing'])
LiteralString = namedtuple('LiteralString', ['content'])
DefaultArg = namedtuple('DefaultArg', ['content'])
FunctionIdentifier = namedtuple('FunctionIdentifier',['kit','module','function'])
Alias = namedtuple('Alias',['name'])
FunctionCall = namedtuple('FunctionCall', ['identifier', 'arguments'])
Step = namedtuple('Step', ['action'])