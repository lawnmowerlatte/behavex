Feature: Test feature A4

    Background:
        Given I set up feature A4
    
    Scenario: I test feature A4
        When I enable feature A1
        And I enable feature A4
        Then I see feature A4 is enabled
        And I see feature A4 works
        And I run Python code
            """
            import datetime
            print(datetime.datetime.now())
            print(context.feature_settings.keys())
            context.feature_settings["A0"] = "disable"
            """
        Then I see feature A0 is disabled