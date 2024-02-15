Welcome to <name>, a (windows-only) pyton/selenium script that consumes Nimbus desktop experiment slugs to generate user IDs for every branch and create user.js files for easier enrollment.

The user.js files are created in separate folders with the same name as the branches to avoid confusion.

## Prerequisites
- [Python 3](https://www.python.org/downloads/windows/)
- [Geckodriver](https://github.com/mozilla/geckodriver)
- other?

## Commands
The script uses pytest to wait for the user to input parameters. the current options are:
- ```--env``` requires one of the following Nimbus environment where the recipe is located: ```prod```, ```prod-preview```, ```stage```, or ```stage-preview```

- ```--slug``` requires the slug found on the experiment's Nimbus page

Example command: ```pytest --env prod --slug restore-fxa-toolbar-menu-desktop-existing-users```

## Notes
- Avoid performing any actions while the script is running, as it might interfere with ID generation due to the nature of having to use a Firefox browser console.
- Make sure the Experiment you are targeting is either Live or in Preview and that it has reached the appropriate Remote Settings collection.
