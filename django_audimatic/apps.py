from collections import OrderedDict

from django.apps import AppConfig
from django.db.migrations import state
from django.db.models import options
from django.db.backends.signals import connection_created

if "triggers" not in state.DEFAULT_NAMES:  # pragma: no branch
    state.DEFAULT_NAMES = tuple(state.DEFAULT_NAMES) + ("triggers",)
if "triggers" not in options.DEFAULT_NAMES:  # pragma: no branch
    options.DEFAULT_NAMES = tuple(options.DEFAULT_NAMES) + ("triggers",)

if "audit_table" not in options.DEFAULT_NAMES:  # pragma: no branch
    options.DEFAULT_NAMES = tuple(options.DEFAULT_NAMES) + (
        "audit_table",
        "audit_options",
    )
if "audit_table" not in state.DEFAULT_NAMES:  # pragma: no branch
    state.DEFAULT_NAMES = tuple(state.DEFAULT_NAMES) + (
        "audit_table",
        "audit_options",
    )


def patch_migrations():
    """
    Patch the autodetector and model state detection if migrations are turned on
    """
    if "triggers" not in state.DEFAULT_NAMES:  # pragma: no branch
        state.DEFAULT_NAMES = tuple(state.DEFAULT_NAMES) + ("triggers",)

    if "audit_table" not in state.DEFAULT_NAMES:  # pragma: no branch
        state.DEFAULT_NAMES = tuple(state.DEFAULT_NAMES) + (
            "audit_table",
            "audit_options",
        )

    if "triggers" not in options.DEFAULT_NAMES:  # pragma: no branch
        options.DEFAULT_NAMES = tuple(options.DEFAULT_NAMES) + ("triggers",)
    if "audit_table" not in options.DEFAULT_NAMES:  # pragma: no branch
        options.DEFAULT_NAMES = tuple(options.DEFAULT_NAMES) + (
            "audit_table",
            "audit_options",
        )


class DjangoAudimaticConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_audimatic"

    def ready(self):
        """
        Do all necessary patching
        """

        from django.apps import apps
        from django.conf import settings

        patch_migrations()

        # Set DB defaults so new connections inherit correct settings
        for db_conf in settings.DATABASES.values():
            db_conf.setdefault('TEST', {})['SERIALIZE'] = False
            db_conf['DISABLE_SERVER_SIDE_CURSORS'] = True

        # Helper to patch connections (existing & new)
        def _configure_connection(sender, connection, **kwargs):  # noqa: D401
            # Disable server-side cursors & chunked reads, and disable test serialization
            if hasattr(connection.features, "can_use_chunked_reads"):
                connection.features.can_use_chunked_reads = False
            connection.settings_dict.setdefault("TEST", {})["SERIALIZE"] = False
            connection.settings_dict["DISABLE_SERVER_SIDE_CURSORS"] = True

        from django.db import connections
        for conn in connections.all():
            _configure_connection(None, conn)
        connection_created.connect(_configure_connection, dispatch_uid="audimatic_connection_cfg", weak=False)

        dirty = False

        if "pgtrigger" not in settings.INSTALLED_APPS:
            settings.INSTALLED_APPS.append("pgtrigger")
            dirty = True

        if "nonrelated_inlines" not in settings.INSTALLED_APPS:
            settings.INSTALLED_APPS.append("nonrelated_inlines")
            dirty = True

        if dirty:
            apps.app_configs = OrderedDict()
            apps.apps_ready = apps.models_ready = apps.loading = apps.ready = False
            apps.clear_cache()
            apps.populate(settings.INSTALLED_APPS)
