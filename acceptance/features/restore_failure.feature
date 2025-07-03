Feature: Restore failure handling

  Scenario: AuditActions restore failure logs and raises runtime error
    Given a failing restore operation is set up
    When I attempt to restore with a logging failure
    Then a RuntimeError should be raised during restore