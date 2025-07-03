"""When steps."""
from behave import when, given
from testapp.models import CustomUser, UserAuditTrail

@when('I change the "{model_name}" username to "{username}" and create an audit entry for the change')
def step_impl(context, model_name, username):
    """Change username, save, and create audit entry."""
    instance = context.instance
    old_username = instance.username
    before = {"id": str(instance.id), "username": old_username}
    instance.username = username
    instance.save()
    after = {"id": str(instance.id), "username": username}
    # Create audit entry
    audit_entry = UserAuditTrail.objects.create(
        before=before,
        after=after,
    )
    context.audit_entry = audit_entry
    context.after = after

@when("I retrieve the audit trail for the instance")
def step_impl(context):
    """Retrieve audit trail for the instance."""
    instance = context.instance
    context.audit_trail = instance.get_audit_trail()

@when("I delete the instance and create an audit entry for the deletion")
@given("I delete the instance and create an audit entry for the deletion")
def step_impl(context):
    """Delete instance and add audit entry for deletion."""
    instance = context.instance
    before = {"id": str(instance.id), "username": instance.username}
    instance.delete()
    # Create audit entry for deletion
    audit_entry = UserAuditTrail.objects.create(
        before=before,
        after={},
    )
    context.audit_entry = audit_entry
    context.before = before

@when("I restore the instance from the last audit entry")
@given("I restore the instance from the last audit entry")
def step_impl(context):
    """Restore the instance from the last audit entry."""
    audit_entry = getattr(context, "audit_entry", None)
    if not audit_entry and hasattr(context, "audit_trail"):
        audit_entry = context.audit_trail[0]
    # Assume CustomUser has a restore classmethod
    context.restored = CustomUser.restore(audit_entry)

@when("I run system checks on that model")
def step_impl(context):
    """Run system checks on the bad model."""
    context.errors = context.bad_model.check()