# Created by billschumacher at 9/6/2023
Feature: Django admin model tests

  Scenario: Test User model has an audit trail
    Given a "User" model is available
    Then the "User" model should have an audit trail
