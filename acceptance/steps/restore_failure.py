import pytest
from behave import given, when, then

@given("a failing restore operation is set up")
def given_failing_restore_operation(context):
    context.failure_setup = True

@when("I attempt to restore with a logging failure")
def when_restore_with_logging_failure(context):
    class AuditActions:
        def restore(self):
            raise RuntimeError("Logging failed during restore")
    context.audit_actions = AuditActions()

@then("a RuntimeError should be raised during restore")
def then_runtime_error_raised(context):
    with pytest.raises(RuntimeError, match="Logging failed during restore"):
        context.audit_actions.restore()