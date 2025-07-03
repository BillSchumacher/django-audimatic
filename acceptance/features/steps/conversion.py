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

# --- New steps for enhanced coverage ---

@when('I convert the string "True" for a boolean field')
def when_convert_true_bool(context):
    raw = {'bool_field': 'True'}
    context.converted_true_bool = context.conversion_model._dict_to_field_values(raw)

@then('the bool_field value should be True')
def then_true_bool_value(context):
    test = context.test
    cv = context.converted_true_bool
    test.assertIn('bool_field', cv)
    test.assertIsInstance(cv['bool_field'], bool)
    test.assertTrue(cv['bool_field'])

@when('I convert a dictionary with an unknown field')
def when_convert_unknown_field(context):
    raw = {
        'int_field': '1',
        'unknown_field': 'should_ignore'
    }
    context.converted_unknown_field = context.conversion_model._dict_to_field_values(raw)

@then('the unknown field should be ignored in the result')
def then_unknown_field_ignored(context):
    test = context.test
    cv = context.converted_unknown_field
    test.assertNotIn('unknown_field', cv)
    test.assertIn('int_field', cv)
    test.assertEqual(cv['int_field'], 1)

from django.test import override_settings

@when('I convert a date string with custom format "20/10/2023"')
def when_convert_custom_date_format_override(context):
    raw = {'date_field': '20/10/2023'}
    # Patch the DATE_INPUT_FORMATS to include the custom format
    with override_settings(DATE_INPUT_FORMATS=['%d/%m/%Y', '%Y-%m-%d']):
        context.converted_custom_date = context.conversion_model._dict_to_field_values(raw)

@then('the date_field should be converted to the correct date')
def then_custom_date_converted_override(context):
    test = context.test
    cv = context.converted_custom_date
    test.assertIn('date_field', cv)
    test.assertIsInstance(cv['date_field'], date)
    test.assertEqual(cv['date_field'], date(2023, 10, 20))

@when('I convert a datetime string with custom format "20/10/2023 16:31:22"')
def when_convert_custom_datetime_format_override(context):
    raw = {'dt_field': '20/10/2023 16:31:22'}
    # Patch the DATETIME_INPUT_FORMATS to include the custom format
    with override_settings(DATETIME_INPUT_FORMATS=['%d/%m/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S']):
        context.converted_custom_datetime = context.conversion_model._dict_to_field_values(raw)

@then('the dt_field should be converted to the correct datetime')
def then_custom_datetime_converted_override(context):
    test = context.test
    cv = context.converted_custom_datetime
    test.assertIn('dt_field', cv)
    test.assertIsInstance(cv['dt_field'], datetime)
    test.assertEqual(cv['dt_field'], datetime(2023, 10, 20, 16, 31, 22))