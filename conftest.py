import sys
import pytest
import pygetwindow as GW
import pyautogui
import requests
import json
import pyperclip
import time
import os
import pathlib
import glob


# Set the current Remote Settings endpoints
prod_link = 'https://firefox.settings.services.mozilla.com/v1/buckets/main/collections/nimbus-desktop-experiments/records'
prod_preview_link = 'https://firefox.settings.services.mozilla.com/v1/buckets/main/collections/nimbus-preview/records'
stage_link = 'https://firefox.settings.services.allizom.org/v1/buckets/main/collections/nimbus-desktop-experiments/records'
stage_preview_link = 'https://firefox.settings.services.allizom.org/v1/buckets/main/collections/nimbus-preview/records'

@pytest.fixture(scope="class", autouse=True)
def check_env_param(env):
    # Dynamic endpoint selection based on provided environment in --env and checking for a valid env
    if env == "prod":
        return requests.get(prod_link)
    elif env == "prod-preview":
        return requests.get(prod_preview_link)
    elif env == "stage":
        return requests.get(stage_link)
    elif env == "stage-preview":
        return requests.get(stage_preview_link)
    else:
        sys.exit("Invalid environment!")


@pytest.fixture(scope="class", autouse=True)
def check_slug_param(check_env_param, slug):
    # Pulling the selected endpoint, filtering the recipe's json based on the slug and checking if it's valid
    experiment_slug = slug
    rs_payload = check_env_param.json()

    filtered_entries = [entry for entry in rs_payload['data'] if entry[
        'slug'] == experiment_slug]
    try:
        extracted_dict = filtered_entries[0]
        return {
            "extracted_dict": extracted_dict,
            "experiment_slug": experiment_slug
        }
    except IndexError:
        sys.exit("Invalid Slug!")

def firefox_profile():
    profile_path = os.getenv('APPDATA') + "\Mozilla\Firefox\Profiles"
    script_path = pathlib.Path(__file__).parent.resolve()
    firefox_path = str(script_path) + '\\core'

    profile_list = os.listdir(profile_path)
    check_for_idgen = [fn for fn in profile_list if 'IDGEN' in fn]

    create_build_command = 'cmd /c "firefox.exe -p -CreateProfile IDGEN"'
    open_build_command = 'cmd /c "firefox.exe -no-remote -p IDGEN -jsconsole"'

    # Checking if a Firefox IDGEN profile exists, in not, creating a new one with the required user.js
    if not check_for_idgen:
        print('\n No IDGEN profile found')

        os.chdir(firefox_path)
        os.system(create_build_command)

        gen_profile_path = str(glob.glob(profile_path + '\\*IDGEN'))
        gen_profile_path = gen_profile_path.replace("[", "")
        gen_profile_path = gen_profile_path.replace("]", "")
        gen_profile_path = gen_profile_path.replace("'", "")

        os.chdir(gen_profile_path)
        idgen_userjs = open("user.js", "a")
        idgen_userjs.writelines([f'user_pref("devtools.chrome.enabled", true);', '\nuser_pref("browser.shell.checkDefaultBrowser", false);'])
        idgen_userjs.close()
        print('\n IDGEN profile created')

        os.chdir(firefox_path)
        os.system(open_build_command)

    else:
        print('\n IDGEN profile found')
        os.chdir(firefox_path)
        os.system(open_build_command)

@pytest.fixture()
def setup_function(env, slug, check_slug_param):

    # Defining the user ID generation code snippet parts
    pre_command1 = 'Cu.import("resource://gre/modules/Console.jsm");'
    pre_command2 = 'Cu.import("resource://nimbus/lib/ExperimentManager.jsm");'
    post_command = 'ExperimentManager.generateTestIds({...recipe, ...recipe.bucketConfig}).then(console.log)'

    firefox_profile()

    # Formatting the json output and assembling the code snippet
    formatted_json = json.dumps(check_slug_param['extracted_dict'], separators=(',', ':'), ensure_ascii=False)
    full_recipe = f"recipe = {formatted_json}"
    id_command = pre_command1 + pre_command2 + full_recipe

    # Focusing the browser console, entering the code snippet and copying the output
    time.sleep(1)
    browser_console_window = GW.getWindowsWithTitle("Parent process Browser Console")[0]
    browser_console_window.activate()

    pyautogui.write(id_command)
    pyautogui.hotkey("shift", "enter")
    pyautogui.write(post_command)
    pyautogui.press("enter")
    if len(id_command) > 4000:
        time.sleep(20)
    if len(id_command) < 2000:
        time.sleep(10)
    else:
        time.sleep(15)
    pyautogui.press("tab")
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "c")
    ids_raw = pyperclip.paste()
    pyautogui.hotkey('alt', 'f4')
    pyautogui.hotkey('alt', 'f4')
    print("\nGenerated the following IDs:")
    return {
        "rawid": ids_raw,
        "experiment_slug": check_slug_param['experiment_slug'],
        "environment": env
    }

def pytest_addoption(parser):
    # Defining user input parameters
    parser.addoption("--env")
    parser.addoption("--slug")
    parser.addoption("--region")

@pytest.fixture(scope="class", autouse=True)
def env(request):
    return request.config.getoption("--env")

@pytest.fixture(scope="class", autouse=True)
def slug(request):
    return request.config.getoption("--slug")

@pytest.fixture(scope="class", autouse=True)
def region(request):
    return request.config.getoption("--region")