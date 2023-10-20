from string import printable
from pyparsing import Forward, Combine, Word, OneOrMore, White, Optional, Literal, delimitedList, quotedString, alphas, alphanums, oneOf, StringEnd
from parser_types import LiteralString, Variable, VariableAssignment, DataStream, DefaultArg, Token, Alias, FunctionIdentifier, FunctionCall, Index, DefaultIndexString
from index_handelers import flattened_index_handlers_dict

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

default_index_string = Combine(OneOrMore(Word(printable, excludeChars="{}") | White())).setParseAction(lambda t: DefaultIndexString(t[0]))


prefixes = ' '.join(flattened_index_handlers_dict.keys())

EXPR_PREFIX = oneOf(prefixes, caseless=True)

index = Forward()

variable = (Literal("$") + identifier("var_name") + Optional(Literal(":") + index("index"))).setParseAction(lambda t: Variable(t.var_name, t.index))
token = (Literal("%") + Optional(index("path"))).setParseAction(lambda t: Token("%", t.path))
data_stream = (Literal("@") + identifier("name") + LPAR + Optional(delimitedList(literal_string | variable | default_arg | token))("args") + RPAR).setParseAction(lambda t: DataStream(t.name, t.args.asList()))

index << (
    EXPR_PREFIX("prefix") +
    LBRACE + (literal_string | variable | data_stream | token | default_index_string)("content") + RBRACE
).setParseAction(lambda t: Index(t.prefix, t.content[0]))

variable_assignment = (
    Literal("$") + identifier("var_name") + 
    Optional(Literal(":") + index("index")) + LPAR + 
    (literal_string | variable | data_stream | token | default_arg)("value") + RPAR
).setParseAction(lambda t: VariableAssignment(t.var_name, t.index[0] if t.index else '', t.value[0]))

function_identifier = (identifier("kit") + DOT + identifier("module") + DOT + identifier("function")).setParseAction(lambda t: FunctionIdentifier(t.kit, t.module,t.function))

alias = Word(printable, excludeChars="(")("alias").setParseAction(lambda t: Alias(t.alias))

function_call = (
    (function_identifier | alias)("identifier") +
    LPAR +
    Optional(delimitedList(literal_string | variable | data_stream | token | default_arg))("arguments") + RPAR
).setParseAction(lambda t: FunctionCall(t.identifier[0], t.arguments.asList()))

workflow = delimitedList(data_stream | variable_assignment | function_call, ARROW) + StringEnd()
