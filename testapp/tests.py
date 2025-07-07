from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Project, ProjectAuditTrail, CustomUser

class ProjectM2MAuditTest(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(username="user1", password="foo")
        self.user2 = CustomUser.objects.create_user(username="user2", password="bar")
        self.project = Project.objects.create(name="Test project")

    def test_m2m_audit_trail(self):
        # Add a member
        self.project.members.add(self.user1)
        # Remove a member
        self.project.members.remove(self.user1)
        # Add a member back and add another
        self.project.members.add(self.user1, self.user2)
        # Remove one member
        self.project.members.remove(self.user2)

        trail = self.project.get_audit_trail()
        self.assertTrue(trail.count() > 0, "Audit trail should have at least one entry for m2m changes")
        found = False
        for row in trail:
            if any(k.startswith("members_") for k in row.before.keys()) or any(k.startswith("members_") for k in row.after.keys()):
                found = True
                break
        self.assertTrue(found, "Audit trail should contain m2m member keys like 'members_1' in before/after")
