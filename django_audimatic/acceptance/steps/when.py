"""When steps."""
from behave import when, given
from testapp.models import CustomUser, UserAuditTrail

def _to_hstore(data: dict) -> str:
    """Serializes a dict to a Postgres hstore string."""
    if not data:
        return ""
    return ",".join([f'"{k}"=>"{v}"' for k, v in data.items()])

@when('I change the "{model_name}" username to "{username}" and create an audit entry for the change')
def when_change_username(context, model_name, username):
    """Change username, save, and create audit entry."""
    instance = context.instance
    old_username = instance.username
    before = {"id": str(instance.id), "username": old_username}
    instance.username = username
    instance.save()
    after = {"id": str(instance.id), "username": username}
    # Create audit entry with hstore strings
    audit_entry = UserAuditTrail.objects.create(
        before=_to_hstore(before),
        after=_to_hstore(after),
    )
    context.audit_entry = audit_entry
    context.after = after

@when("I retrieve the audit trail for the instance")
def when_retrieve_audit_trail(context):
    """Retrieve audit trail for the instance."""
    instance = context.instance
    context.audit_trail = instance.get_audit_trail()

@when("I delete the instance and create an audit entry for the deletion")
@given("I delete the instance and create an audit entry for the deletion")
def given_when_delete_instance(context):
    """Delete instance and add audit entry for deletion."""
    instance = context.instance
    before = {"id": str(instance.id), "username": instance.username}
    instance.delete()
    # Create audit entry for deletion with after=''
    audit_entry = UserAuditTrail.objects.create(
        before=_to_hstore(before),
        after='',
    )
    context.audit_entry = audit_entry
    context.before = before

@when("I restore the instance from the last audit entry")
@given("I restore the instance from the last audit entry")
def when_restore_instance(context):
    """Restore the instance from the last audit entry."""
    audit_entry = getattr(context, "audit_entry", None)
    if not audit_entry and hasattr(context, "audit_trail"):
        audit_entry = context.audit_trail[0]
    # Assume CustomUser has a restore classmethod
    context.restored = CustomUser.restore(audit_entry)

@when("I run system checks on that model")
def when_run_system_checks(context):
    """Run system checks on the bad model."""
    context.errors = context.bad_model.check()