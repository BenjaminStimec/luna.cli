from string import printable
from pyparsing import Forward, Combine, Word, OneOrMore, White, Optional, Literal, delimitedList, quotedString, alphas, alphanums, Group, oneOf, SkipTo
from parser_types import LiteralString, Variable, VariableAssignment, DataStream, DefaultArg, Token, Alias

LPAR = "("
RPAR = ")"
ARROW = "=>"
DOT = "."
COMMA = ","
LBRACK = "["
RBRACK = "]"
LBRACE = "{"
RBRACE = "}"
DOTS = "..."

identifier = Word(alphas, alphanums + "_")

literal_string = quotedString.setParseAction(lambda t: LiteralString(t[0][1:-1]))
default_arg = Combine(OneOrMore(Word(printable, excludeChars=",()") | White())).setParseAction(lambda t: DefaultArg(t[0]))


EXPR_PREFIX = oneOf('J X L')

extended_expr = Group(
    EXPR_PREFIX("expr_type") +
    LBRACE + SkipTo(RBRACE) + RBRACE
)
 
variable = (Literal("$") + identifier("var_name") + Optional(Literal(":") + extended_expr("index"))).setParseAction(lambda t: Variable(t.var_name, t.index))
data_stream = (Literal("@") + identifier + LPAR + Optional(delimitedList(literal_string | variable | default_arg)) + RPAR).setParseAction(lambda t: DataStream(t[1]))
token = (Literal("%") + Optional(extended_expr("path"))).setParseAction(lambda t: Token("%", t.path))

variable_assignment = (
    Literal("$") + identifier("var_name") + LPAR + 
    token("output") + RPAR
).setParseAction(lambda t: VariableAssignment(t.var_name, t.output))

alias = (identifier("kit") + DOT + identifier("module") + DOT + identifier("function")).setParseAction(lambda t: Alias(t.kit, t.module,t.function))

alias = (identifier("kit") + DOT + identifier("module") + DOT + identifier("function")).setParseAction(lambda t: Alias(t.kit, t.module,t.function))

function_call = Group(
    delimitedList(identifier("kit") + DOT + identifier("module") + DOT + identifier("function") | DOTS + identifier("alias")) +
    LPAR +
    Optional(delimitedList(literal_string | variable | data_stream | token | default_arg))("arguments") + RPAR
)
workflow = Group(delimitedList(function_call | variable_assignment, ARROW))("workflow")
