import sys
import pytest
import pygetwindow as GW
import pyautogui
import requests
import time
import os
import pathlib
import glob
import pyperclip


# Set the current Remote Settings endpoints
prod_link = 'https://firefox.settings.services.mozilla.com/v1/buckets/main/collections/nimbus-desktop-experiments/records'
prod_preview_link = 'https://firefox.settings.services.mozilla.com/v1/buckets/main/collections/nimbus-preview/records'
stage_link = 'https://firefox.settings.services.allizom.org/v1/buckets/main/collections/nimbus-desktop-experiments/records'
stage_preview_link = 'https://firefox.settings.services.allizom.org/v1/buckets/main/collections/nimbus-preview/records'
prod_secured_experiments_link = 'https://firefox.settings.services.mozilla.com/v1/buckets/main/collections/nimbus-secure-experiments/records'
stage_secured_experiments_link = 'https://firefox.settings.services.allizom.org/v1/buckets/main/collections/nimbus-secure-experiments/records'

@pytest.fixture(scope="class", autouse=True)
def check_env_param(env):
    # Dynamic endpoint selection based on provided environment in --env and checking for a valid env
    if env == "prod":
        endpoint_url = prod_link
        return {
            "records": requests.get(prod_link),
            "endpoint_url": endpoint_url
        }
    elif env == "prod-preview":
        endpoint_url = prod_preview_link
        return {
            "records": requests.get(prod_preview_link),
            "endpoint_url": endpoint_url
        }
    elif env == "stage":
        endpoint_url = stage_link
        return {
            "records": requests.get(stage_link),
            "endpoint_url": endpoint_url
        }
    elif env == "stage-preview":
        endpoint_url = stage_preview_link
        return {
            "records": requests.get(stage_preview_link),
            "endpoint_url": endpoint_url
        }
    elif env == "prod-secured":
        endpoint_url = prod_secured_experiments_link
        return {
            "records": requests.get(prod_secured_experiments_link),
            "endpoint_url": endpoint_url
        }
    elif env == "stage-secured":
        endpoint_url = stage_secured_experiments_link
        return {
            "records": requests.get(stage_secured_experiments_link),
            "endpoint_url": endpoint_url
        }
    else:
        sys.exit("Invalid environment!")


@pytest.fixture(scope="class", autouse=True)
def check_slug_param(check_env_param, slug):
    # Pulling the selected endpoint, filtering the recipe's json based on the slug and checking if it's valid
    experiment_slug = slug
    rs_payload = check_env_param['records'].json()

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
    profile_path = os.getenv('APPDATA') + r"\Mozilla\Firefox\Profiles"
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
        idgen_userjs.writelines([f'user_pref("devtools.chrome.enabled", true);', '\nuser_pref("browser.shell.checkDefaultBrowser", false);', '\nuser_pref("app.update.enabled", false);'])
        idgen_userjs.close()
        print('\n IDGEN profile created')

        os.chdir(firefox_path)
        os.system(open_build_command)

    else:
        print('\n IDGEN profile found')
        os.chdir(firefox_path)
        os.system(open_build_command)


@pytest.fixture()
def setup_function(env, slug, check_slug_param, check_env_param):

    firefox_profile()

    # Assembling the code snippet
    selected_endpoint_url = check_env_param['endpoint_url']
    id_command = f'await ChromeUtils.importESModule("resource://nimbus/ExperimentAPI.sys.mjs").ExperimentAPI.manager.generateTestIds((await (await fetch ("{selected_endpoint_url}/{slug}")).json()).data)'

    # Focusing the browser console, entering the code snippet and copying the output
    while True:
        try:
            browser_console_window = GW.getWindowsWithTitle("Parent process Browser Console")[0]
        except IndexError:
            time.sleep(1)
        else:
            browser_console_window.activate()
            break

    time.sleep(1)
    pyperclip.copy(id_command)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")
    time.sleep(1)
    pyautogui.press("tab")
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "c")
    ids_raw = pyperclip.paste()
    browser_console_window.close()
    firefox_window = GW.getWindowsWithTitle("Firefox Nightly")[0]
    firefox_window.close()
    print("\n Generated the following IDs:")
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
