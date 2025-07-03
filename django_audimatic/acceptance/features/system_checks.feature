Feature: AuditTrigger system checks

  Scenario: Model missing audit table raises error
    Given a model missing an audit table is defined
    When I run system checks on that model
    Then an error "django_audimatic.E001" should be reported

  Scenario: Model missing triggers raises error
    Given a model missing triggers is defined
    When I run system checks on that model
    Then an error "django_audimatic.E002" should be reported