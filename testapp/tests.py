from django.test import TestCase, skipUnlessDBFeature
from django.contrib.auth import get_user_model
from django_audimatic.models import AuditActions
from testapp.models import CustomUser, UserAuditTrail

@skipUnlessDBFeature('has_hstore')
class AuditRestoreTestCase(TestCase):
    def test_restore_from_audit_reverts_field_and_records_action(self):
        # Step a: Create a CustomUser
        user = CustomUser.objects.create_user(username='foo', email='initial@example.com', password='password')

        # Step b: Update the user's email
        user.email = 'changed@example.com'
        user.save()

        # Step c: Retrieve the latest audit record (should be for update)
        audit_row = UserAuditTrail.objects.order_by('-id').first()
        self.assertIsNotNone(audit_row)
        # The 'before' hstore should contain the initial state
        self.assertEqual(audit_row.before.get('email'), 'initial@example.com')
        self.assertEqual(audit_row.after.get('email'), 'changed@example.com')

        # Step d: Call restore_from_audit to revert email
        user.restore_from_audit(audit_row_id=audit_row.pk, fields=['email'])

        # Step e: Refresh from db and assert email reverted
        user.refresh_from_db()
        self.assertEqual(user.email, 'initial@example.com')

        # Step f: Assert AuditActions row created
        action_row = AuditActions.objects.order_by('-id').first()
        self.assertIsNotNone(action_row)
        self.assertEqual(action_row.action, 'restore')
        self.assertEqual(action_row.audit_table, UserAuditTrail._meta.db_table)
        self.assertEqual(action_row.audit_row_id, audit_row.pk)
