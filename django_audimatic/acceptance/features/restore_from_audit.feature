Feature: Restore from audit trail

  Scenario: Restore a user email to a previous state.
    Given a user exists with username "foo" and email "initial@example.com"
    When I update the user's email to "changed@example.com"
    And I restore the user's email from the latest audit row
    Then the user's email should be "initial@example.com"
    And an AuditActions record should exist for the restore linked to the audit row