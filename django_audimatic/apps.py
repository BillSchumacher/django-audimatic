from django.apps import AppConfig

from django.db.migrations import state
from django.db.models import options


if "triggers" not in state.DEFAULT_NAMES:  # pragma: no branch
    state.DEFAULT_NAMES = tuple(state.DEFAULT_NAMES) + ("triggers",)

if "audit_table" not in options.DEFAULT_NAMES:  # pragma: no branch
    options.DEFAULT_NAMES = tuple(options.DEFAULT_NAMES) + ("audit_table", "audit_options",)


def patch_migrations():
    """
    Patch the autodetector and model state detection if migrations are turned on
    """
    if "triggers" not in state.DEFAULT_NAMES:  # pragma: no branch
        state.DEFAULT_NAMES = tuple(state.DEFAULT_NAMES) + ("triggers",)

    if "audit_table" not in options.DEFAULT_NAMES:  # pragma: no branch
        options.DEFAULT_NAMES = tuple(options.DEFAULT_NAMES) + ("audit_table", "audit_options",)


class DjangoAudimaticConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_audimatic'

    def ready(self):
        """
        Do all necessary patching
        """
        patch_migrations()
