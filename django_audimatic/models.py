from django.db import models
from django.contrib.postgres.fields import HStoreField
import pgtrigger


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


class AuditTrigger(models.Model):

    class Meta:
        abstract = True
        triggers = [
            pgtrigger.Trigger(
                name="track_history_create",
                level=pgtrigger.Row,
                when=pgtrigger.After,
                operation=pgtrigger.Insert,
                func=pgtrigger.Func(TRIGGER_SQL)
            ),
            pgtrigger.Trigger(
                name="track_history_update",
                level=pgtrigger.Row,
                when=pgtrigger.After,
                operation=pgtrigger.Update,
                func=pgtrigger.Func(TRIGGER_SQL)
            ),
            pgtrigger.Trigger(
                name="track_history_delete",
                level=pgtrigger.Row,
                when=pgtrigger.After,
                operation=pgtrigger.Delete,
                func=pgtrigger.Func(TRIGGER_SQL)
            )
        ]
