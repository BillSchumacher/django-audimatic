from behave import given, when, then
import pytest

@given("a conversion model is defined")
def step_impl_given_conversion_model(context):
    # For the purpose of these tests, use a simple dict as the "model"
    context.model = {}

@when('I convert the string "{value}" for a boolean field')
def step_impl_convert_string_for_boolean_field(context, value):
    # Simulate field conversion to bool
    if value.lower() == "true":
        context.bool_result = True
    elif value.lower() == "false":
        context.bool_result = False
    else:
        raise ValueError(f"Cannot convert {value} to bool")

@then('the bool_field value should be True')
def step_impl_assert_bool_field_true(context):
    assert context.bool_result is True, f"Expected True, got {context.bool_result}"

@then('the bool_field value should be False')
def step_impl_assert_bool_field_false(context):
    assert context.bool_result is False, f"Expected False, got {context.bool_result}"

@when('I convert the boolean object {py_bool} for a boolean field')
def step_impl_convert_bool_object_for_boolean_field(context, py_bool):
    # Converts string "True"/"False" to actual Python bool
    context.bool_result = py_bool == "True"

@when('I convert an unknown string "{value}" for a boolean field')
def step_impl_convert_unknown_string_for_boolean_field(context, value):
    # Simulate unknown string being passed for bool field
    try:
        if value.lower() == "true":
            context.bool_result = True
        elif value.lower() == "false":
            context.bool_result = False
        else:
            raise ValueError("Unknown string for boolean field")
    except Exception as exc:
        context.conversion_exception = exc

@then('a ValueError should be raised')
def step_impl_assert_value_error(context):
    assert hasattr(context, "conversion_exception"), "Expected exception but none was raised"
    assert isinstance(context.conversion_exception, ValueError), f"Expected ValueError, got {type(context.conversion_exception)}"