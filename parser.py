from string import printable
from pyparsing import Or, Combine, Word, OneOrMore, White, Optional, Literal, delimitedList, quotedString, alphas, alphanums, oneOf, SkipTo, StringEnd
from parser_types import LiteralString, Variable, VariableAssignment, DataStream, DefaultArg, Token, Alias, FunctionIdentifier, FunctionCall, Step

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


EXPR_PREFIX = oneOf('J X L')

extended_expr = (
    EXPR_PREFIX("expr_type") +
    LBRACE + SkipTo(RBRACE) + RBRACE
)
 
variable = (Literal("$") + identifier("var_name") + Optional(Literal(":") + extended_expr("index"))).setParseAction(lambda t: Variable(t.var_name, t.index))
token = (Literal("%") + Optional(extended_expr("path"))).setParseAction(lambda t: Token("%", t.path))
data_stream = (Literal("@") + identifier("name") + LPAR + Optional(delimitedList(literal_string | variable | default_arg | token))("args") + RPAR).setParseAction(lambda t: DataStream(t.name, t.args))


variable_assignment = (
    Literal("$") + identifier("var_name") + LPAR + 
    token("output") + RPAR
).setParseAction(lambda t: VariableAssignment(t.var_name, t.output))

function_identifier = (identifier("kit") + DOT + identifier("module") + DOT + identifier("function")).setParseAction(lambda t: FunctionIdentifier(t.kit, t.module,t.function))

alias = Word(printable, excludeChars="(")("alias").setParseAction(lambda t: Alias(t.alias))

function_call = (
    (function_identifier | alias)("identifier") +
    LPAR +
    Optional(delimitedList(literal_string | variable | data_stream | token | default_arg))("arguments") + RPAR
).setParseAction(lambda t: FunctionCall(t.identifier[0], t.arguments.asList()))

workflow = delimitedList(variable_assignment | function_call, ARROW) + StringEnd()
