import ast
import pytest

from django_audimatic.models import AuditTrigger
from behave import given, when, then

@given("a conversion helper model exists")
def given_conversion_helper_model(context):
    context.model = AuditTrigger

@when('I ensure_dict parses the hstore string "{hstore_string}"')
@when('I parse the hstore string "{hstore_string}"')
def when_ensure_dict_parses_hstore_string(context, hstore_string):
    # Call AuditTrigger._ensure_dict directly
    context.ensure_dict_result = AuditTrigger._ensure_dict(hstore_string)

@then("the ensure_dict result should be the dictionary {expected_dict}")
@then('the result should be the dictionary {expected_dict}')
def then_assert_ensure_dict_result(context, expected_dict):
    expected = ast.literal_eval(expected_dict)
    result = context.ensure_dict_result
    assert result == expected, f"Expected {expected}, got {result}"

@when('I ensure_dict parses the AST dict string "{ast_string}"')
@when('I parse the AST dict string "{ast_string}"')
def when_ensure_dict_parses_ast_string(context, ast_string):
    # Should parse as dict via ast.literal_eval for legacy/oddball strings
    context.ensure_dict_result = AuditTrigger._ensure_dict(ast_string)

@then("the ensure_dict (AST) result should be the dictionary {expected_dict}")
@then('the result should be the dictionary {expected_dict}')
def then_assert_ensure_dict_ast_result(context, expected_dict):
    expected = ast.literal_eval(expected_dict)
    result = context.ensure_dict_result
    assert result == expected, f"Expected {expected}, got {result}"

@when("I ensure_dict parses a non-coercible object")
@when("I parse a non-coercible object")
def when_ensure_dict_parses_noncoercible_object(context):
    class NonDict:
        pass
    context.ensure_dict_result = AuditTrigger._ensure_dict(NonDict())

@then("the ensure_dict result should be an empty dictionary")
@then("the result should be an empty dictionary")
def then_assert_ensure_dict_empty(context):
    assert context.ensure_dict_result == {}, f"Expected empty dict, got {context.ensure_dict_result}"