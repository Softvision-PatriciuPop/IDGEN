import pytest
import re
from pathlib import Path
from termcolor import colored


class TestUserJsGeneration:
    @pytest.mark.usefixtures("setup_function")
    def test_user_js_creation(self, setup_function, region):
        # Filtering console output to include only the user IDs
        pattern = re.compile(r'Object\s*{([^}]*)}', re.DOTALL)
        match = pattern.findall(setup_function['rawid'])

        result_list = []

        # Splitting the output in keys and values
        for item in match:
            key_value_pairs = [pair.strip() for pair in item.split(',')]

            result_dict = {}

            # Extracting the keys and adding them to a dictionary
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

        # Creating folders for the experiment
        parent_folder_name = setup_function['experiment_slug']
        parent_folder_path = Path.home() / "Desktop" / parent_folder_name
        parent_folder_path.mkdir(parents=True, exist_ok=True)

        # Creating user.js files and folders for each branch
        counter = 0
        for i in list_keys:
            child_folder_name = i.replace('"', "")
            child_folder_path = parent_folder_path / child_folder_name
            child_folder_path.mkdir(parents=True, exist_ok=True)

            split_id = list_values[counter]
            with open(child_folder_path / "user.js", "x") as file:
                file.write(f'user_pref("app.normandy.user_id", {split_id});')
                # Adding stage endpoint + hash
                if setup_function['environment'] == 'stage' or 'stage-preview':
                    file.write(f'\nuser_pref("security.content.signature.root_hash", "3C:01:44:6A:BE:90:36:CE:A9:A0:9A:CA:A3:A5:20:AC:62:8F:20:A7:AE:32:CE:86:1C:B2:EF:B7:0F:A0:C7:45");')
                    file.write(f'\nuser_pref("services.settings.server", "https://firefox.settings.services.allizom.org/v1");')
                # Adding preview collection for prod/stage
                if setup_function['environment'] == 'stage-preview' or 'prod-preview':
                    file.write(f'\nuser_pref("messaging-system.rsexperimentloader.collection_id", "nimbus-preview");')
                # Adding browser search region
                if region is not None:
                    file.write(f'\nuser_pref("browser.search.region", "{region}");')

            counter += 1
        print('\n User.js files created')
        print(colored('\n --------DONE!--------', 'green'))