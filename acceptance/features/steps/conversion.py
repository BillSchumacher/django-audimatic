from behave import given, when, then
from django_audimatic.models import AuditTrigger
from django.db import models
from datetime import date, datetime

class ConversionModel(AuditTrigger):
    int_field = models.IntegerField()
    float_field = models.FloatField()
    dec_field = models.DecimalField(max_digits=10, decimal_places=2)
    bool_field = models.BooleanField()
    date_field = models.DateField()
    dt_field = models.DateTimeField()

    class Meta(AuditTrigger.Meta):
        app_label = 'django_audimatic'
        audit_table = None

@given('a conversion model is defined')
def given_conversion_model(context):
    context.conversion_model = ConversionModel

@when('I convert a representative set of string values')
def when_convert_values(context):
    raw = {
        'int_field': '42',
        'float_field': '3.14',
        'dec_field': '99.95',
        'bool_field': 'False',
        'date_field': '2023-10-20',
        'dt_field': '2023-10-20 15:30:45',
    }
    context.converted = context.conversion_model._dict_to_field_values(raw)

@then('the returned values should match expected Python types')
def then_returned_types(context):
    cv = context.converted
    test = context.test
    test.assertIsInstance(cv['int_field'], int)
    test.assertEqual(cv['int_field'], 42)
    test.assertIsInstance(cv['float_field'], float)
    test.assertIsInstance(cv['dec_field'], float)  # Decimal converted to float by helper
    test.assertIsInstance(cv['bool_field'], bool)
    test.assertFalse(cv['bool_field'])
    from datetime import date, datetime
    test.assertIsInstance(cv['date_field'], date)
    test.assertIsInstance(cv['dt_field'], datetime)

@when('I attempt to convert an invalid boolean string')
def when_convert_invalid_bool(context):
    raw = {'bool_field': 'notbool'}
    context.error = None
    try:
        context.conversion_model._dict_to_field_values(raw)
    except ValueError as e:
        context.error = e

@then('a ValueError should be raised')
def then_valueerror(context):
    context.test.assertIsNotNone(context.error)

@when('I attempt to restore using a non-existent audit id {audit_id:d}')
def when_restore_nonexistent_id(context, audit_id):
    from testapp.models import CustomUser
    context.restore_result = CustomUser.restore(audit_id)

@then('the restore result should be None')
def then_restore_none(context):
    context.test.assertIsNone(context.restore_result)