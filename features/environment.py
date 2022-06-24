import json
import re
import os
import time
import inspect
import random
import os.path
import logging.config

from pprint import pprint, pformat
from functools import wraps

from behave import use_step_matcher, use_fixture
from behave.step_registry import registry as the_step_registry
from behave.contrib.scenario_autoretry import patch_scenario_with_autoretry

use_step_matcher("re")


def fuzz(value, min_percentage=75, max_percentage=150):
    multiplier = random.randrange(min_percentage, max_percentage)
    fuzzed = value * multiplier / 100
    return fuzzed


def sleep(duration):
    duration = float(duration)
    fuzzed = fuzz(duration)
    time.sleep(fuzzed)
    return fuzzed


def before_all(context):
    context.feature_settings = {}
    context.feature_setup_multiplier = 1


def after_step(context, step):
    step.duration += sleep(1)


def get_estimates_from_tags(tags):
    estimate = 0
    
    for tag in tags:
        key, value = tag.split("=", 1)
        if key == "estimate":
            estimate += int(value)

    return estimate


def estimate_step(estimate, arg_multiplier=None):
    """
    Decorator for step definition functions which provides a way to estimate the duration of the step.
    The values assigned to the function are used later by the `estimate_feature(feature)` function.
    """
    def step_decorator(step_fn):
        step_fn.estimate = estimate
        step_fn.arg_multiplier = arg_multiplier
        return step_fn
    return step_decorator


def estimate_feature(feature):
    """
    This function provides a heuristic for estimating feature durations based on the following inputs:
        - `@estimate=n tags` in the feature files on either features or scenarios
            - Feature tags are only counted once per feature, not per scenario
        - `@estimate(value, arg_multiplier)` decorators in the step definition
            - If only `value` is provided, it is a static value
            - If `arg_multiplier` is provided, the integer value of the argument specified is multiplied by the value
    """
    feature_estimate = get_estimates_from_tags(feature.tags)
        
    for scenario in feature:
        feature_estimate += get_estimates_from_tags(scenario.tags)
        
        for test_step in scenario:
            match = the_step_registry.find_match(test_step)
            if match is not None:
                fn = match.func
                # Check if the function has been decorated with @estimate
                if "arg_multiplier" in dir(fn) and fn.arg_multiplier is not None:
                    # Check the scaling factor variable is in the function signature
                    try:
                        arg_index = inspect.getargspec(fn).args.index(fn.arg_multiplier)
                    except ValueError:
                        print(f"Argument specified as multiplication factor {fn.arg_multiplier} is not present in the argument list")
                        raise RuntimeError(f"Argument specified as scaling factor {fn.arg_multiplier} is not present in the argument list")
                    
                    # Check the arguments provided contain the argument in the expected position
                    try:
                        arg_value = match.arguments[arg_index - 1].value
                    except IndexError:
                        print(f"Argument position {arg_index} indicated by the index was not present in the argument list")
                        raise RuntimeError(f"Argument position {arg_index} indicated by the index was not present in the argument list")
                    
                    # Check that the value provided is an integer
                    try:
                        multiplier = int(arg_value)
                    except ValueError:
                        print(f"Argument provided for multiplier value {arg_value} was not an integer")
                        raise RuntimeError(f"Argument provided for multiplier value {arg_value} was not an integer")
                else:
                    multiplier = 1

                minimum_step_estimate = .5
                step_estimate = 0
                
                if "estimate" in dir(fn):
                    step_estimate += fn.estimate
                
                step_estimate = step_estimate * multiplier
                
                step_estimate = max(step_estimate, minimum_step_estimate)
                    
                feature_estimate += step_estimate
                
    print(f"Feature: {str(feature)}: {feature_estimate}")
    return feature_estimate
    