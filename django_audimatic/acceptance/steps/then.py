"""Then steps."""
from behave import then

@then('the "{model_name}" model should have an audit trail')
def step_impl(context, model_name):
    """Check that the model has an audit trail."""
    model = context.models[model_name]
    context.test.assertTrue(hasattr(model, "get_audit_trail"))

@then('the audit diff should contain key "{key}" with value "{value}"')
def step_impl(context, key, value):
    """Check the audit diff contains the expected key-value pair."""
    audit_trail = context.audit_trail
    diff = audit_trail[0].diff if hasattr(audit_trail[0], "diff") else audit_trail[0].after_data
    context.test.assertIsInstance(diff, dict, "Diff is not a dictionary")
    context.test.assertIn(key, diff, f"Key '{key}' not in diff: {diff}")
    context.test.assertEqual(diff.get(key), value, f"Expected diff[{key}] == '{value}', got {diff.get(key)}")

@then('the instance should exist with username "{username}"')
def step_impl(context, username):
    """Assert that a CustomUser instance exists with the given username."""
    context.test.assertTrue(
        CustomUser.objects.filter(username=username).exists(),
        f"User with username '{username}' does not exist"
    )

@then('an error "{error_id}" should be reported')
def step_impl(context, error_id):
    """Check that the specified error id is in the reported errors."""
    errors = context.errors
    found = any(e.get("id") == error_id for e in errors)
    context.test.assertTrue(
        found,
        f"Expected error id '{error_id}' in errors: {errors}"
    )