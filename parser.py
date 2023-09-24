from string import printable
from collections import namedtuple
from pyparsing import *
from parser_types import LiteralString, Variable, VariableAssignment, DataStream, DefaultArg, PreviousOutput

LPAR = "("
RPAR = ")"
ARROW = "=>"
DOT = "."
COMMA = ","
LBRACK = "["
RBRACK = "]"
LBRACE = "{"
RBRACE = "}"

identifier = Word(alphas, alphanums + "_")

literal_string = quotedString.setParseAction(lambda t: LiteralString(t[0][1:-1]))
default_arg = Combine(OneOrMore(Word(printable, excludeChars=",()") | White())).setParseAction(lambda t: DefaultArg(t[0]))
variable = (Literal("$") + identifier).setParseAction(lambda t: Variable(t[1]))
data_stream = (Literal("@") + identifier + LPAR + Optional(delimitedList(literal_string | variable | default_arg)) + RPAR).setParseAction(lambda t: DataStream(t[1]))
previous_output = (Literal("%") + default_arg).setParseAction(lambda t: PreviousOutput(t[1].content))
variable_assignment = (
    Literal("$") + identifier("var_name") + LPAR + 
    previous_output("output") + RPAR
).setParseAction(lambda t: VariableAssignment(t.var_name, t.output))

# TODO: foreach - execute the rest of the workflow for each element of a list
function_call = Group(
    identifier("kit") + DOT +
    identifier("module") + DOT +
    identifier("function") + LPAR +
    Optional(delimitedList(literal_string | variable | data_stream | previous_output | default_arg))("arguments") + RPAR
)
workflow = Group(delimitedList(function_call | variable_assignment, ARROW))("workflow")