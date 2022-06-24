Feature: Test feature B3

    Background:
        Given I set up feature B3
    
    Scenario: I test feature B3
        When I enable feature B3
        And I wait 5 seconds
        Then I see feature B3 is enabled
        And I wait 15 seconds
        And I see feature B3 works
