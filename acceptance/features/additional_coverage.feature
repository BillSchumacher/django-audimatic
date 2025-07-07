Feature: Additional coverage for utility functions

  # _ensure_dict branches
  Scenario: ensure_dict returns empty dict for None
    When I ensure_dict is called with None
    Then the ensure_dict output should equal {}

  Scenario: ensure_dict converts object with items()
    When I ensure_dict is called with an items object
    Then the ensure_dict output should equal {"k": "v"}

  Scenario: ensure_dict handles hstore NULL and booleans
    When I ensure_dict is called with hstore string '"a"=>"NULL","b"=>"true","c"=>"false"'
    Then the ensure_dict output should equal {"a": None, "b": "true", "c": "false"}

  Scenario: ensure_dict falls back to ast literal
    When I ensure_dict is called with literal string "{'x': 1}"
    Then the ensure_dict output should equal {"x": 1}

  Scenario: ensure_dict fallback dict(raw) failure returns empty
    When I ensure_dict is called with a non coercible object
    Then the ensure_dict output should equal {}

  # _dict_to_field_values branches
  Scenario: _dict_to_field_values handles None value
    Given a conversion model is defined
    When I convert dict {'float_field': None}
    Then the converted dict should equal {'float_field': None}

  Scenario: int conversion failure falls back to string
    Given a conversion model is defined
    When I convert dict {'int_field': 'notint'}
    Then the converted int_field should equal 'notint'

  Scenario: invalid boolean stored as original string
    Given a conversion model is defined
    When I convert dict {'bool_field': 'maybe'}
    Then the converted bool_field should equal 'maybe'

  # restore_from_audit branches
  Scenario: restore returns None for missing audit id
    Given a "CustomUser" instance with username "missing" exists
    When I call restore with non existent audit id 999999
    Then the restore result should be None

  Scenario: restore handles insert audit when object missing
    Given a "CustomUser" instance with username "insertcase" exists
    When I create insert style audit and restore
    Then the restore result should be None

  Scenario: restore handles update audit when object missing
    Given a "CustomUser" instance with username "updatecase" exists
    When I create update style audit and restore
    Then the restore result should be None