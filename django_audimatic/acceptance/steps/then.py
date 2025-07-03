"""Then steps."""
from behave import then
from testapp.models import CustomUser
from django_audimatic.models import AuditTrigger

@then('the "{model_name}" model should have an audit trail')
def step_impl(context, model_name):
    """Check that the model has an audit trail."""
    model = context.models[model_name]
    context.test.assertTrue(hasattr(model, "get_audit_trail"))

@then('the audit diff should contain key "{key}" with value "{value}"')
def step_impl(context, key, value):
    """Check the audit diff contains the expected key-value pair in any entry of audit_trail."""
    audit_trail = context.audit_trail
    found = False
    for entry in audit_trail:
        diff = entry.diff if hasattr(entry, "diff") else getattr(entry, "after", None)
        after_dict = AuditTrigger._ensure_dict(entry.after) if hasattr(entry, "after") else {}
        actual_value = diff.get(key) if isinstance(diff, dict) and key in diff else after_dict.get(key)
        if str(actual_value) == value:
            found = True
            break
    context.test.assertTrue(
        found,
        f"Expected value for key '{key}' is '{value}', but it was not found in any audit trail entry."
    )

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