# Created by billschumacher at 9/6/2023
Feature: Django admin model tests

  Scenario: Test User model has an audit trail
    Given a "CustomUser" model is available
    Then the "CustomUser" model should have an audit trail
