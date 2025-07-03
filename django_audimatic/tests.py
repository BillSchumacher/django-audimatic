from django.test import TestCase
from django.db import models, transaction, connection
from django.contrib.auth import get_user_model
from django_audimatic.models import AuditTrigger, AuditTrail, AuditActions

# Test models for auditing
class UserAuditTrail(AuditTrail):
    pass

class User(AuditTrigger):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)

    class Meta(AuditTrigger.Meta):
        audit_table = UserAuditTrail

# -- Tests --

class AuditRestoreTests(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create(username="alice", email="alice@example.com", is_active=True)
        # Simulate audit log for initial insert
        self.audit_entry_insert = UserAuditTrail.objects.create(before={}, after={
            "id": str(self.user.id),
            "username": self.user.username,
            "email": self.user.email,
            "is_active": str(self.user.is_active),
        })
        # Simulate audit log for update
        self.user.username = "bob"
        self.user.is_active = False
        self.user.save()
        self.audit_entry_update = UserAuditTrail.objects.create(before={
            "id": str(self.user.id),
            "username": "alice",
            "email": "alice@example.com",
            "is_active": "True",
        }, after={
            "id": str(self.user.id),
            "username": "bob",
            "email": "alice@example.com",
            "is_active": "False",
        })
        # Simulate audit log for deletion
        user_id = self.user.id
        self.user.delete()
        self.audit_entry_delete = UserAuditTrail.objects.create(before={
            "id": str(user_id),
            "username": "bob",
            "email": "alice@example.com",
            "is_active": "False",
        }, after={})

    def test_restore_deleted_user(self):
        # Confirm user is deleted
        self.assertFalse(User.objects.filter(id=self.audit_entry_delete.before["id"]).exists())
        # Restore from deletion audit
        restored = User.restore(self.audit_entry_delete)
        self.assertIsNotNone(restored)
        self.assertEqual(restored.id, int(self.audit_entry_delete.before["id"]))
        self.assertEqual(restored.username, self.audit_entry_delete.before["username"])
        self.assertFalse(restored.is_active)
        # AuditActions should be created
        action = AuditActions.objects.latest('id')
        self.assertEqual(action.action, "restore")
        self.assertEqual(action.audit_row_id, self.audit_entry_delete.id)

    def test_restore_update(self):
        # User was deleted in setUp, recreate for update test
        user = User.objects.create(
            id=int(self.audit_entry_update.after["id"]),
            username=self.audit_entry_update.after["username"],
            email=self.audit_entry_update.after["email"],
            is_active=self.audit_entry_update.after["is_active"] == "True"
        )
        # Apply restore to 'before' state
        restored = User.restore(self.audit_entry_update)
        self.assertIsNotNone(restored)
        self.assertEqual(restored.username, self.audit_entry_update.before["username"])
        self.assertTrue(restored.is_active)
        # AuditActions should be created
        action = AuditActions.objects.latest('id')
        self.assertEqual(action.audit_row_id, self.audit_entry_update.id)

    def test_restore_insert(self):
        # User exists, now restore using insert audit (should delete)
        user_id = int(self.audit_entry_insert.after["id"])
        self.assertTrue(User.objects.filter(id=user_id).exists())
        restored = User.restore(self.audit_entry_insert)
        self.assertIsNone(restored)
        self.assertFalse(User.objects.filter(id=user_id).exists())
        # AuditActions should be created
        action = AuditActions.objects.latest('id')
        self.assertEqual(action.audit_row_id, self.audit_entry_insert.id)

# --- Additional Coverage ---

class AuditTrailDiffAnnotationTests(TestCase):
    def test_get_audit_trail_diff_annotation(self):
        # Create initial user
        user = User.objects.create(username="alice", email="alice@example.com", is_active=True)
        # Simulate audit entry with username changed from "alice" to "bob"
        audit_entry = UserAuditTrail.objects.create(
            before={
                "id": str(user.id),
                "username": "alice",
                "email": "alice@example.com",
                "is_active": "True",
            },
            after={
                "id": str(user.id),
                "username": "bob",
                "email": "alice@example.com",
                "is_active": "True",
            }
        )
        # Fetch audit trail and check diff
        qs = user.get_audit_trail()
        self.assertEqual(qs.count(), 1)
        diff = qs[0].diff  # Should be a dict with key "username": "bob"
        self.assertIsInstance(diff, dict)
        self.assertIn("username", diff)
        self.assertEqual(diff["username"], "bob")

from django.core.checks import Error

class SystemCheckErrorTests(TestCase):
    def test_missing_audit_table_error(self):
        # Define AuditTrigger subclass without audit_table
        class BadModelMissingAuditTable(AuditTrigger):
            field = models.CharField(max_length=10)
            class Meta(AuditTrigger.Meta):
                app_label = "django_audimatic_test"
                # audit_table intentionally omitted

        errors = BadModelMissingAuditTable.check()
        error_ids = [e.id for e in errors]
        self.assertIn("django_audimatic.E001", error_ids)
        # Optional: Check error message content
        for e in errors:
            if e.id == "django_audimatic.E001":
                self.assertIn("audit_table", e.msg.lower())

    def test_missing_triggers_error(self):
        # Define valid AuditTrail subclass
        class ValidTrail(AuditTrail):
            pass

        # Define AuditTrigger subclass with triggers intentionally set empty
        class BadModelMissingTriggers(AuditTrigger):
            field = models.CharField(max_length=10)
            class Meta(AuditTrigger.Meta):
                audit_table = ValidTrail
                triggers = []  # intentionally empty
                app_label = "django_audimatic_test"

        errors = BadModelMissingTriggers.check()
        error_ids = [e.id for e in errors]
        self.assertIn("django_audimatic.E002", error_ids)
        # Optional: Check error message content
        for e in errors:
            if e.id == "django_audimatic.E002":
                self.assertIn("triggers", e.msg.lower())
