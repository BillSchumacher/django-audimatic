"""Then steps."""
from behave import then
from django.db import connection
from testapp.models import CustomUser, UserAuditTrail
from django_audimatic.models import AuditActions


@then('the "{model_name}" model should have an audit trail')
def step_impl(context, model_name):
    """Check that the model has an audit trail."""
    model = context.models[model_name]
    context.test.assertTrue(hasattr(model, "get_audit_trail"))


@then('the user\'s email should be "{expected_email}"')
def step_then_user_email_should_be(context, expected_email):
    if connection.vendor != "postgresql":
        context.scenario.skip("This scenario requires PostgreSQL.")
    user = context.user
    user.refresh_from_db()
    assert user.email == expected_email, f"Expected email {expected_email}, got {user.email}"

@then('an AuditActions record should exist for the restore linked to the audit row')
def step_then_audit_action_exists(context):
    if connection.vendor != "postgresql":
        context.scenario.skip("This scenario requires PostgreSQL.")
    audit_row = context.latest_audit_row
    action_row = AuditActions.objects.order_by('-id').first()
    assert action_row is not None, "No AuditActions record found"
    assert action_row.action == 'restore', f"Expected action 'restore', got {action_row.action}"
    assert action_row.audit_table == UserAuditTrail._meta.db_table, \
        f"Expected audit_table {UserAuditTrail._meta.db_table}, got {action_row.audit_table}"
    assert action_row.audit_row_id == audit_row.pk, \
        f"Expected audit_row_id {audit_row.pk}, got {action_row.audit_row_id}"
