import pytest
from behave import given, when, then
from unittest.mock import patch
from testapp.models import CustomUser

@given("a failing restore operation is set up")
def given_failing_restore_operation(context):
    # Create a CustomUser and a real audit entry for restore
    context.user = CustomUser.objects.create(username="failrestore")
    # Simulate an audit entry; this should mimic your model's audit entry creation
    from django_audimatic.models import AuditActions
    context.audit_entry = AuditActions.objects.create(
        action='restore',
        content_object=context.user,
        changes={},
        user=None
    )

@when("I attempt to restore with a logging failure")
def when_restore_with_logging_failure(context):
    # Patch the audit logging method used during restore to raise a RuntimeError
    from django_audimatic.models import AuditActions

    def fail_logging(*args, **kwargs):
        raise RuntimeError("Logging failed during restore")

    # Try patching a likely audit logging method; fallback to objects.create if needed
    patch_target = None
    if hasattr(AuditActions, "log_restore_action"):
        patch_target = "django_audimatic.models.AuditActions.log_restore_action"
    else:
        patch_target = "django_audimatic.models.AuditActions.objects.create"

    patcher = patch(patch_target, side_effect=fail_logging)
    context._patcher = patcher
    patcher.start()

    # Attempt to restore; should raise when logging is attempted
    context.restore_exception = None
    try:
        CustomUser.restore(context.audit_entry)
    except Exception as e:
        context.restore_exception = e

@then("a RuntimeError should be raised during restore")
def then_runtime_error_raised(context):
    # Stop patcher if running
    if hasattr(context, "_patcher"):
        context._patcher.stop()
    assert isinstance(context.restore_exception, RuntimeError), f"Expected RuntimeError, got {context.restore_exception}"
    assert str(context.restore_exception) == "Logging failed during restore"