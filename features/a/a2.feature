Feature: Test feature A2

    Background:
        Given I set up feature A2
    
    Scenario: I test feature A2
        When I enable feature A1
        And I enable feature A2
        Then I see feature A2 is enabled
        And I see feature A2 works
