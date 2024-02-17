Welcome to <name>, a (windows-only) python script that consumes Nimbus desktop experiment slugs to generate user IDs for every branch and create user.js files. Compatible with stage/prod as well as preview environemnts, it can also set extra values in the user.js files for easier enrollment.

The user.js files are created in separate folders with the same name as the branches to avoid confusion.

## Prerequisites
- Make sure you have [Python 3](https://www.python.org/downloads/windows/) and ```pip``` installed.
- Download any version of the Firefox Nightly build.

## Installation
1. Download and extract the content of the repository in a folder.
2. Place the ```core``` folder of the downloaded Nightly build in the chosen folder.
3. Open a terminal and run the following command to install all dependencies ```pip install -r requirements.txt```

## Generating user IDs
The script uses pytest to wait for the user to input parameters. To run the script open a new terminal and write ```pytest``` followed by any of the following commands:
- ```--env``` - requires the environment where the recipe is located. The options are: ```prod```, ```prod-preview```, ```stage```, or ```stage-preview```
- ```--slug``` requires the slug found on the experiment's Nimbus page e.g. ```--slug ppop-grand-ui-check```
- ```--region``` - OPTIONAL, sets the browser's search region to the provided string e.g. ```--region US```

Example command: ```pytest --env prod --slug restore-fxa-toolbar-menu-desktop-existing-users```

## Notes
- Avoid performing any actions while the script is running, as it might interfere with ID generation due to the nature of having to use a Firefox browser console.
- Make sure the Experiment you are targeting is either Live or in Preview and that it has reached the appropriate Remote Settings collection.
- For the preview collections, the script automatically changes the Nimbus collection preferences to ```nimbus-preview```
- The script only works with Desktop experiments, for mobile experiments please use nimbus-cli.
