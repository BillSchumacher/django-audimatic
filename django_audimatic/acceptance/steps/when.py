from behave import when
from django.db import connection
from testapp.models import UserAuditTrail

@when('I update the user\'s email to "{new_email}"')
def step_when_update_email(context, new_email):
    if connection.vendor != "postgresql":
        context.scenario.skip("This scenario requires PostgreSQL.")
    user = context.user
    user.email = new_email
    user.save()

@when('I restore the user\'s email from the latest audit row')
def step_when_restore_email_from_audit(context):
    if connection.vendor != "postgresql":
        context.scenario.skip("This scenario requires PostgreSQL.")
    user = context.user
    audit_row = UserAuditTrail.objects.order_by('-id').first()
    user.restore_from_audit(audit_row_id=audit_row.pk, fields=['email'])
    context.latest_audit_row = audit_row