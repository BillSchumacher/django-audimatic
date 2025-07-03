"""

"""
from __future__ import annotations

import pgtrigger
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import HStoreField
from django.core import checks
from django.db import models
from django.db.models import ExpressionWrapper, F


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

    @staticmethod
    def _ensure_dict(raw) -> dict:
        """
        Ensures that the input is a dict.
        If it's a string (such as serialized hstore), attempts to parse using regex for key=>value pairs.
        Falls back to ast.literal_eval for legacy or odd encodings.
        If input is already a dict, returns it as-is.
        """
        import ast
        import re

        if isinstance(raw, dict):
            return raw
        if raw is None:
            return {}

        # If it's already an HStore-like dict
        if hasattr(raw, "items"):
            return dict(raw.items())

        # If it's a string, try regex for key=>value pairs
        if isinstance(raw, str):
            # Improved regex: key=>value pairs, allowing quoted/unquoted, optional spaces, robust comma delimiting
            # e.g. 'foo => "bar", "baz"=>123'
            pattern = r'\s*(".*?"|\w+)\s*=>\s*(NULL|".*?"|\d+|true|false|\w+)\s*(?:,|$)'
            matches = re.findall(pattern, raw)
            if matches:
                result = {}
                for k, v in matches:
                    k = k.strip('"') if k.startswith('"') and k.endswith('"') else k
                    if v == "NULL":
                        result[k] = None
                    elif v.startswith('"') and v.endswith('"'):
                        result[k] = v.strip('"')
                    elif v in ("true", "false"):
                        result[k] = v
                    else:
                        result[k] = v
                return result
            # Fall back to ast.literal_eval as last resort
            try:
                parsed = ast.literal_eval(raw)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass
        # If it's something else, try to coerce to dict.
        try:
            return dict(raw)
        except Exception:
            return {}

    @classmethod
    def _dict_to_field_values(cls, data) -> dict:
        """
        Convert hstore dict (all string values) to correct Python types for model fields.
        For initial version, only attempts numeric and boolean conversion; else leaves as string.
        """
        data = cls._ensure_dict(data)
        if not data:
            return {}

        field_values = {}
        for key, value in data.items():
            try:
                field = cls._meta.get_field(key)
            except Exception:
                continue  # skip fields not on the model

            # Only convert if not None
            if value is None:
                field_values[key] = None
                continue

            internal_type = field.get_internal_type()
            try:
                if internal_type in ("IntegerField", "BigIntegerField", "SmallIntegerField", "PositiveIntegerField", "PositiveSmallIntegerField", "AutoField"):
                    field_values[key] = int(value)
                elif internal_type in ("FloatField", "DecimalField"):
                    field_values[key] = float(value)
                elif internal_type == "BooleanField":
                    field_values[key] = value in ("True", "true", "1")
                else:
                    field_values[key] = value
            except Exception:
                field_values[key] = value
        return field_values

    def restore_from_audit(self, audit_row_id: int, fields: list[str] | None = None, user=None):
        """
        Restore selected fields of this object from a specific audit row entry.
        Only updates the provided fields, does not recreate or delete the object.
        Logs the partial_restore action.
        """
        audit_table = self.get_audit_table()
        if audit_table is None:
            raise ValueError("Audit table not configured for this model.")

        audit_row = audit_table.objects.get(pk=audit_row_id)
        before = self._ensure_dict(audit_row.before)
        after = self._ensure_dict(audit_row.after)

        # Choose snapshot: if audit_row.before['id'] == str(self.id) then use before, else after
        snapshot = before if before.get("id") == str(self.id) else after
        snapshot = self._ensure_dict(snapshot)

        available_fields = set(snapshot.keys()) - {"id"}
        if fields is not None:
            target_fields = available_fields & set(fields)
        else:
            target_fields = available_fields

        for field in target_fields:
            value_str = snapshot[field]
            converted = self.__class__._dict_to_field_values({field: value_str})[field]
            setattr(self, field, converted)
        self.save()

        # Log the action
        AuditActions.objects.create(
            action="partial_restore",
            audit_table=audit_table._meta.db_table,
            audit_row_id=audit_row.id,
            user=user,
        )
        return self

    @classmethod
    def restore(cls, audit_entry, user=None):
        """
        Restore the object state to the state captured by the audit_entry.
        If audit_entry is an int, loads from audit table.
        Returns the affected object (or None if not applicable).
        """
        audit_table = cls.get_audit_table()
        if audit_table is None:
            raise ValueError("Audit table not configured for this model.")

        # Load the audit entry if pk is given
        if isinstance(audit_entry, int):
            audit_row = audit_table.objects.using("default").get(pk=audit_entry)
        else:
            audit_row = audit_entry

        before = dict(audit_row.before or {})
        after = dict(audit_row.after or {})

        # Determine type of audit event
        before_has_id = before.get("id") is not None
        after_has_id = after.get("id") is not None

        obj = None

        if before_has_id and not after_has_id:
            # Deletion: recreate object from before
            field_values = cls._dict_to_field_values(before)
            obj = cls.objects.using("default").create(**field_values)
            action = "restore"
        elif not before_has_id and after_has_id:
            # Insertion: remove the inserted object
            try:
                obj = cls.objects.using("default").get(pk=after["id"])
                obj.delete()
            except cls.DoesNotExist:
                obj = None
            action = "restore"
        elif before_has_id and after_has_id:
            # Update: set fields to 'before' values
            try:
                obj = cls.objects.using("default").get(pk=before["id"])
                field_values = cls._dict_to_field_values(before)
                for k, v in field_values.items():
                    setattr(obj, k, v)
                obj.save()
            except cls.DoesNotExist:
                obj = None
            action = "restore"
        else:
            # Unrecognized or empty entry
            action = "restore"
            obj = None

        # Log the restore action
        AuditActions.objects.using("default").create(
            action=action,
            audit_table=audit_table._meta.db_table,
            audit_row_id=audit_row.id,
            user=user,
        )
        return obj

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
