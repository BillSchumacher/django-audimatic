from __future__ import annotations

import pgtrigger
from weakref import WeakKeyDictionary

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import HStoreField
from django.core import checks
from django.db import models
from django.db.models import ExpressionWrapper, F
from django.db.models.signals import m2m_changed


class AuditTrail(models.Model):
    """
    An audit trail model mixin, no fields except for a timestamp
    perhaps should be added to tables that utilize this.

    If this data will be accessed frequently consider an IndexedAuditTrail instead.
    """

    before = HStoreField()
    after = HStoreField()

    class Meta:
        abstract = True


class IndexedAuditTrail(models.Model):
    """
    An indexed audit trail model mixin, no fields except for a timestamp
    perhaps should be added to tables that utilize this.
    """

    before = HStoreField(db_index=True)
    after = HStoreField(db_index=True)

    class Meta:
        abstract = True


TRIGGER_SQL = """
    INSERT INTO {meta.audit_table._meta.db_table}(before, after)
        SELECT hstore(old), hstore(new);
    RETURN new;
"""

CRUD_TRIGGERS = [
    pgtrigger.Trigger(
        name="track_history_create",
        level=pgtrigger.Row,
        when=pgtrigger.After,
        operation=pgtrigger.Insert,
        func=pgtrigger.Func(TRIGGER_SQL),
    ),
    pgtrigger.Trigger(
        name="track_history_update",
        level=pgtrigger.Row,
        when=pgtrigger.After,
        operation=pgtrigger.Update,
        func=pgtrigger.Func(TRIGGER_SQL),
    ),
    pgtrigger.Trigger(
        name="track_history_delete",
        level=pgtrigger.Row,
        when=pgtrigger.After,
        operation=pgtrigger.Delete,
        func=pgtrigger.Func(TRIGGER_SQL),
    ),
]


class AuditTrigger(models.Model):
    """ """

    class Meta:
        abstract = True
        triggers = CRUD_TRIGGERS
        audit_table = None

    @classmethod
    def check(cls, **kwargs):
        """

        :param kwargs:
        :return:
        """
        errors = super().check(**kwargs)
        errors.extend(cls._check_audit_table(**kwargs))
        errors.extend(cls._check_audit_triggers(**kwargs))
        return errors

    @classmethod
    def _check_audit_table(cls, **kwargs) -> list[checks.Error]:
        """

        :param kwargs:
        :return:
        """
        audit_table = cls.get_audit_table()
        if not audit_table:
            return [
                checks.Error(
                    "no audit table.",
                    hint=f"No audit table defined for {cls}, define an audit_table in the Meta class.",
                    obj=cls,
                    id="django_audimatic.E001",
                )
            ]
        return []

    @classmethod
    def _check_audit_triggers(cls, **kwargs) -> list[checks.Error]:
        """

        :param kwargs:
        :return:
        """
        audit_triggers = cls._get_triggers()
        if not audit_triggers:
            return [
                checks.Error(
                    "no triggers.",
                    hint=f"No triggers defined for {cls}, "
                    "does your Meta class inherit from `AuditTrigger.Meta`?",
                    obj=cls,
                    id="django_audimatic.E002",
                )
            ]
        return []

    @classmethod
    def get_audit_table(cls) -> None | models.Model:
        """

        :return:
        """
        return getattr(cls._meta, "audit_table", None)

    @classmethod
    def _get_triggers(cls) -> list:
        """

        :return:
        """
        return getattr(cls._meta, "triggers", None)

    def get_audit_trail(self) -> models.QuerySet:
        """

        :return:
        """
        audit_table = self.get_audit_table()
        pk = self.id
        return (
            (
                audit_table.objects.filter(before__id__contains=pk)
                | audit_table.objects.filter(after__id__contains=pk)
            )
            .annotate(
                diff=ExpressionWrapper(
                    F("after") - F("before"), output_field=HStoreField()
                )
            )
            .all()
        )

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Do not register for abstract classes
        if getattr(cls._meta, 'abstract', False):
            return
        audit_options = getattr(cls._meta, 'audit_options', {})
        track_m2m = audit_options.get('track_m2m', True)
        if not track_m2m:
            return
        # Register m2m signal handlers for all ManyToMany fields
        for field in getattr(cls._meta, 'many_to_many', []):
            m2m_changed.connect(
                _handle_m2m_changed,
                sender=field.remote_field.through,
                weak=False,
            )


class AuditActions(models.Model):
    """Tracks actions performed on a table.

    When a record is restored from an audit trail, etc.
    """

    action = models.CharField(max_length=128)
    audit_table = models.CharField(max_length=128)
    audit_row_id = models.BigIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.DO_NOTHING, null=True, blank=True
    )


# --- M2M Audit Tracking ---

_M2M_BEFORE_CACHE: "WeakKeyDictionary[models.Model, dict[str, set[int]]]" = WeakKeyDictionary()  # pragma: no cover

def _handle_m2m_changed(sender, **kwargs):
    instance = kwargs.get('instance')
    action = kwargs.get('action')
    field = kwargs.get('field')
    # pk_set = kwargs.get('pk_set', set())  # Removed: unused variable for lint compliance
    if not instance or not field:
        return

    field_name = field.name

    # For pre_ actions, store the current relation set
    if action in ('pre_add', 'pre_remove', 'pre_clear'):
        current_ids = set(getattr(instance, field_name).values_list('pk', flat=True))
        if instance not in _M2M_BEFORE_CACHE:
            _M2M_BEFORE_CACHE[instance] = {}
        _M2M_BEFORE_CACHE[instance][field_name] = current_ids

    # For post_ actions, compare and write audit if changed
    elif action in ('post_add', 'post_remove', 'post_clear'):
        before = set()
        before_dict = {}
        after_dict = {}
        if instance in _M2M_BEFORE_CACHE and field_name in _M2M_BEFORE_CACHE[instance]:
            before = _M2M_BEFORE_CACHE[instance][field_name]
        after = set(getattr(instance, field_name).values_list('pk', flat=True))
        if before != after:
            before_dict = {f"{field_name}_{pk}": "1" for pk in before}
            after_dict = {f"{field_name}_{pk}": "1" for pk in after}
            audit_table = instance.get_audit_table()
            if audit_table:
                audit_table.objects.create(before=before_dict, after=after_dict)
        # Clean up
        if instance in _M2M_BEFORE_CACHE and field_name in _M2M_BEFORE_CACHE[instance]:
            del _M2M_BEFORE_CACHE[instance][field_name]
        if instance in _M2M_BEFORE_CACHE and not _M2M_BEFORE_CACHE[instance]:
            del _M2M_BEFORE_CACHE[instance]