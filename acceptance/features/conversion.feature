Feature: Conversion utility

  Scenario: Convert various string values to appropriate field types
    Given a conversion model is defined
    When I convert a representative set of string values
    Then the returned values should match expected Python types

  Scenario: Invalid boolean value raises error
    Given a conversion model is defined
    When I attempt to convert an invalid boolean string
    Then a ValueError should be raised

  Scenario: Restoring with non-existent audit id returns None
    Given a "CustomUser" instance with username "alice" exists
    When I attempt to restore using a non-existent audit id 999999
    Then the restore result should be None