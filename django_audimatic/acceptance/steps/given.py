from behave import given
from django.db import connection
from testapp.models import CustomUser

@given('a user exists with username "{username}" and email "{email}"')
def step_given_user_exists(context, username, email):
    if connection.vendor != "postgresql":
        context.scenario.skip("This scenario requires PostgreSQL.")
    context.user = CustomUser.objects.create_user(username=username, email=email, password="password")