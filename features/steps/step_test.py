from io import StringIO
from contextlib import redirect_stdout

from features.environment import estimate_step as estimate
from features.environment import fuzz, sleep

# import lawnmowerlatte.behave.step_wrappers


@step("I set up feature ([A-Z])([0-9]+)")
@estimate(2, arg_multiplier="feature_level")
def setup(context, feature_class, feature_level):
    sleep(int(feature_level) * context.feature_setup_multiplier)
    print(f"Feature {feature_class}{feature_level} set up")


@estimate(2)
@step("I (enable|disable) feature (.*)")
def change_feature_setting(context, expected_setting, feature_name):
    # Check A1 for all Ax features
    if feature_name[0] == "A" and int(feature_name[1]) > 1 and expected_setting == "enable":
        print(f"Checking A1 for {feature_name}")
        assert "A1" in context.feature_settings.keys(), f"Feature {feature_name} cannot be enabled without feature A1 which has not been initialized"
        assert context.feature_settings["A1"] == "enable", f"Feature {feature_name} cannot be enabled without feature A1 which is not enabled"
    
    # Enabling B1 disables all Bx features
    if feature_name == "B1" and expected_setting == "enable":
        print("Disabling all subfeatures conflicting with B1")
        for key in context.feature_settings.keys():
            if key[0] == "B" and context.feature_settings[key] == "enable":
                context.feature_settings[key] = "disable"

    # Disabling A1 disables all Ax features
    if feature_name == "A1" and expected_setting == "disable":
        print("Disabling all subfeatures of A1")
        for key in context.feature_settings.keys():
            if context.feature_settings[key][0] == "A":
                context.feature_settings[key] = "disable"
    
    print(f"Enabling feature {feature_name}")
    context.feature_settings[feature_name] = expected_setting


@step("I see feature (.*) is (enable|disable)d")
def check_feature_setting(context, feature_name, expected_setting):
    assert feature_name in context.feature_settings.keys(), f"Feature {feature_name} has not be initialized"
    assert context.feature_settings[feature_name] == expected_setting, f"Feature {feature_name} is not {expected_setting}d: {feature_name}:{context.feature_settings[feature_name]}"


@step("I see feature (.*) works")
def check_feature(context, feature_name):
    assert feature_name in context.feature_settings.keys(), f"Feature {feature_name} has not be initialized"
    

@estimate(1, arg_multiplier="delay")
@step("I wait ([0-9]+) seconds")
def wait_n_secs(context, delay):
    sleep(delay)


@step("I do nothing")
def nop(context):
    pass
    
    
@step("I run Python code")
def run_python_code(context):
    def exec_code(code, globals_=None, locals_=None):
        if globals_ is None:
            globals_ = {}
        if locals_ is None:
            locals_ = globals_
        locals_["__file__"] = "run_python_code"
        
        stdout_fd = StringIO()
        with redirect_stdout(stdout_fd):
            exec(code, globals_, locals_)
        stdout = stdout_fd.getvalue()
        
        return stdout
    
    code = context.text
    output = exec_code(code, globals(), locals())
    
    print(output)
    
    