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

  Scenario: Boolean true string is converted to True
    Given a conversion model is defined
    When I convert the string "True" for a boolean field
    Then the bool_field value should be True

  Scenario: Unknown field is ignored in conversion
    Given a conversion model is defined
    When I convert a dictionary with an unknown field
    Then the unknown field should be ignored in the result

  Scenario: Custom date format is parsed when fallback is provided
    Given a conversion model is defined
    When I convert a date string with custom format "20/10/2023"
    Then the date_field should be converted to the correct date