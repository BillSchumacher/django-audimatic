Feature: Audit trail diff and restore

  Scenario: Audit diff shows changed fields
    Given a "CustomUser" instance with username "alice" exists
    When I change the "CustomUser" username to "bob" and create an audit entry for the change
    And I retrieve the audit trail for the instance
    Then the audit diff should contain key "username" with value "bob"

  Scenario: Restore deleted user from audit entry
    Given a "CustomUser" instance with username "alice" exists
    And I delete the instance and create an audit entry for the deletion
    When I restore the instance from the last audit entry
    Then the instance should exist with username "alice"