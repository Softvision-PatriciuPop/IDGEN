from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import pygetwindow as GW
import pyautogui
import requests
import json
import pyperclip
import time
import re
import os
from pathlib import Path


def set_up_ids():
    options = FirefoxOptions()
    options.add_argument("-jsconsole")
    options.set_preference("devtools.chrome.enabled", True)
    driver = webdriver.Firefox(executable_path=r'D:\Work\Selenium\Nimbus Desktop Companion\geckodriver.exe',
                               options=options)

    pre_command1 = 'Cu.import("resource://gre/modules/Console.jsm");'
    pre_command2 = 'Cu.import("resource://nimbus/lib/ExperimentManager.jsm");'
    post_command = 'ExperimentManager.generateTestIds({...recipe, ...recipe.bucketConfig}).then(console.log)'

    driver.get('about:blank')

    # To call pytest addoption
    response_prod = requests.get(
        'https://firefox.settings.services.mozilla.com/v1/buckets/main/collections/nimbus-desktop-experiments/records')
    prod_payload = response_prod.json()
    filtered_entries = [entry for entry in prod_payload['data'] if entry[
        'slug'] == 'restore-fxa-toolbar-menu-panel-on-desktop-existing-users']
    extracted_dict = filtered_entries[0]
    formatted_json = json.dumps(extracted_dict, separators=(',', ':'), ensure_ascii=False)

    full_recipe = f"recipe = {formatted_json}"
    id_command = pre_command1 + pre_command2 + full_recipe
    browser_console_window = GW.getWindowsWithTitle("Browser Console")[0]
    browser_console_window.activate()

    pyautogui.write(id_command)
    pyautogui.hotkey("shift", "enter")
    pyautogui.write(post_command)
    pyautogui.press("enter")
    time.sleep(10)
    pyautogui.press("tab")
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "c")
    ids_raw = pyperclip.paste()
    driver.quit()
    return ids_raw

def create_user_js():
    pattern = re.compile(r'Object\s*{([^}]*)}', re.DOTALL)
    match = pattern.findall(set_up_ids())


    result_list= []

    for item in match:
        key_value_pairs = [pair.strip() for pair in item.split(',')]

        result_dict = {}

        # Extragem key-urile si valorile in dictionar
        for pair in key_value_pairs:
            key, value = pair.split(":", 1)
            result_dict[key.strip()] = value.strip()

        result_list.append(result_dict)

    print(result_list)

    list_keys = None
    list_values = None

    for result_dict in result_list:
        list_keys = list(result_dict.keys())
        list_values = list(result_dict.values())

    parent_folder_name = "slug_name"
    parent_folder_path = Path.home() / "Desktop" / parent_folder_name
    parent_folder_path.mkdir(parents=True, exist_ok=True)

    #cream un folder + user JS in folderul respeciv
    counter = 0
    for i in list_keys:
        child_folder_name = i.replace('"', "")
        child_folder_path = parent_folder_path / child_folder_name
        child_folder_path.mkdir(parents=True, exist_ok=True)

        split_id = list_values[counter]
        with open(child_folder_path / "user.js", "x") as file:
            file.write(f'user_pref("app.normandy.user_id", {split_id});')

        counter += 1

create_user_js()
