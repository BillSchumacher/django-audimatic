Feature: Ensure dictionary conversion utility

  Scenario: Hstore string containing NULL and true/false
    Given a conversion helper model exists
    When I parse the hstore string '"a"=>"NULL","b"=>"true","c"=>"false"'
    Then the result should be the dictionary {"a": None, "b": True, "c": False}

  Scenario: AST literal dict string
    Given a conversion helper model exists
    When I parse the AST dict string "{'foo': 123, 'bar': 'baz'}"
    Then the result should be the dictionary {"foo": 123, "bar": "baz"}

  Scenario: Non-coercible object fallback
    Given a conversion helper model exists
    When I parse a non-coercible object
    Then the result should be an empty dictionary