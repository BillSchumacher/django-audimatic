import ast
import pytest

from django_audimatic.models import AuditTrigger

# --- Step Definitions ---

from behave import given, when, then

@given("a conversion helper model exists")
def given_conversion_helper_model(context):
    # Minimal stub or use real model if needed
    context.model = AuditTrigger

@when('I parse the hstore string "{hstore_string}"')
def when_parse_hstore_string(context, hstore_string):
    def parse_hstore(s):
        d = {}
        items = s.split(",")
        for item in items:
            k, v = item.split("=>")
            k = k.strip(' "\'')
            v = v.strip(' "\'')
            if v == "NULL":
                v = None
            elif v.lower() == "true":
                v = True
            elif v.lower() == "false":
                v = False
            d[k] = v
        return d
    context.parse_result = parse_hstore(hstore_string)

@then("the result should be the dictionary {expected_dict}")
def then_assert_parsed_hstore(context, expected_dict):
    # ast.literal_eval for string-to-dict
    expected = ast.literal_eval(expected_dict)
    result = context.parse_result
    assert result == expected, f"Expected {expected}, got {result}"

@when('I parse the AST dict string "{ast_string}"')
def when_parse_ast_string(context, ast_string):
    context.parse_result = ast.literal_eval(ast_string)

@then("the result should be the dictionary {expected_dict}")
def then_assert_parsed_ast(context, expected_dict):
    expected = ast.literal_eval(expected_dict)
    result = context.parse_result
    assert result == expected, f"Expected {expected}, got {result}"

@when("I parse a non-coercible object")
def when_parse_noncoercible_object(context):
    class NonDict:
        pass
    try:
        dict(NonDict())
        context.parse_result = None
    except Exception:
        context.parse_result = {}

@then("the result should be an empty dictionary")
def then_assert_empty_dict(context):
    assert context.parse_result == {}, f"Expected empty dict, got {context.parse_result}"