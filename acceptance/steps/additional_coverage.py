from behave import when, then, given
from django_audimatic.models import AuditTrigger
from testapp.models import CustomUser, UserAuditTrail
from datetime import date

# ensure_dict related steps

@when("I ensure_dict is called with None")
def when_ensure_dict_none(context):
    context.ensure_out = AuditTrigger._ensure_dict(None)

@then("the ensure_dict output should equal {expected}")
def then_ensure_dict_equals(context, expected):
    context.test.assertEqual(context.ensure_out, eval(expected))

@when("I ensure_dict is called with an items object")
def when_ensure_dict_items(context):
    class ItemsObj:
        def items(self):
            return [("k", "v")]
    context.ensure_out = AuditTrigger._ensure_dict(ItemsObj())

@when('I ensure_dict is called with hstore string {hstore}')
def when_ensure_dict_hstore(context, hstore):
    context.ensure_out = AuditTrigger._ensure_dict(hstore)

@when('I ensure_dict is called with literal string "{literal}"')
def when_ensure_dict_literal(context, literal):
    context.ensure_out = AuditTrigger._ensure_dict(literal)

@when("I ensure_dict is called with a non coercible object")
def when_ensure_dict_noncoercible(context):
    class Foo: pass
    context.ensure_out = AuditTrigger._ensure_dict(Foo())

# _dict_to_field_values steps

@given("a conversion model is defined")
def given_conv_model(context):
    from django.db import models
    class Conv(AuditTrigger):
        int_field = models.IntegerField(null=True)
        float_field = models.FloatField(null=True)
        bool_field = models.BooleanField(null=True)
        class Meta(AuditTrigger.Meta):
            app_label = 'django_audimatic'
            audit_table = None
    context.Conv = Conv

@when("I convert dict {raw_str}")
def when_convert_dict(context, raw_str):
    raw = eval(raw_str)
    context.converted = context.Conv._dict_to_field_values(raw)

@then("the converted dict should equal {expected}")
@then("the converted int_field should equal {expected}")
@then("the converted bool_field should equal {expected}")
def then_converted_equals(context, expected):
    exp = eval(expected)
    if isinstance(exp, dict):
        context.test.assertEqual(context.converted, exp)
    else:
        key = 'int_field' if 'int_field' in context.converted else 'bool_field'
        context.test.assertEqual(context.converted[key], exp)

# restore related

@when("I call restore with non existent audit id {aid:d}")
def when_restore_nonexistent(context, aid):
    context.restored = CustomUser.restore(aid)

@then("the restore result should be None")
def then_restore_none(context):
    context.test.assertIsNone(context.restored)

@when("I create insert style audit and restore")
def when_insert_audit_restore(context):
    user = context.instance
    after = f'"id"=>"{user.id}"'
    entry = UserAuditTrail.objects.create(before='', after=after)
    user.delete()
    context.restored = CustomUser.restore(entry)

@when("I create update style audit and restore")
def when_update_audit_restore(context):
    user = context.instance
    before = f'"id"=>"{user.id}","username"=>"updatecase"'
    after = f'"id"=>"{user.id}","username"=>"update2"'
    entry = UserAuditTrail.objects.create(before=before, after=after)
    user.delete()
    context.restored = CustomUser.restore(entry)