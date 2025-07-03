import pytest
from behave import given, when, then
from unittest.mock import patch
from testapp.models import CustomUser

@given("a failing restore operation is set up")
def given_failing_restore_operation(context):
    # Create a CustomUser and an audit entry (stub/mock as needed)
    context.user = CustomUser.objects.create(username="failrestore")
    context.audit_entry = None  # You would set up an audit entry here as needed

@when("I attempt to restore with a logging failure")
def when_restore_with_logging_failure(context):
    # Monkeypatch AuditActions.objects.create to raise a RuntimeError
    from django_audimatic.models import AuditActions

    def fail_logging(*args, **kwargs):
        raise RuntimeError("Logging failed during restore")

    # Patch the create method on AuditActions.objects
    patcher = patch.object(AuditActions.objects, "create", side_effect=fail_logging)
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