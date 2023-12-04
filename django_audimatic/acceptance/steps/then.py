"""Then steps."""
from behave import then


@then('the "{model_name}" model should have an audit trail')
def step_impl(context, model_name):
    """Check that the model has an audit trail."""
    model = context.models[model_name]
    context.test.assertTrue(hasattr(model, "get_audit_trail"))
