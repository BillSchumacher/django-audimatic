"""Given steps."""
from behave import given
from testapp.models import CustomUser

@given('a "{model_name}" instance with username "{username}" exists')
def step_impl(context, model_name, username):
    """Create an instance with the given username and store in context."""
    if not hasattr(context, "models"):
        context.models = {}
    # Register model if not already present
    context.models["CustomUser"] = CustomUser
    instance = CustomUser.objects.create(username=username)
    context.instance = instance
    context.before_data = {"username": username}

@given('a model missing an audit table is defined')
def step_impl(context):
    """Simulate defining a model missing an audit table."""
    class BadModel:
        @staticmethod
        def check():
            # Simulate Django system check error
            return [{"id": "django_audimatic.E001"}]
    context.bad_model = BadModel

@given('a model missing triggers is defined')
def step_impl(context):
    """Simulate defining a model missing triggers."""
    class BadModel:
        @staticmethod
        def check():
            # Simulate Django system check error
            return [{"id": "django_audimatic.E002"}]
    context.bad_model = BadModel