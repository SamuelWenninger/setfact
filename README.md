# SETFACT
A generic build script that is highly customizable through a JSON settings interface.

## Installation Steps
* Set up ssh-keys on both fonix and VMS
* Install Python 3
* Clone the repo
* Change the first line of the `setfact` script to be the path to your Python executable
* Run `pip install -r requirements.txt` in the repo
* Add the path to the the folder where setfact is to your path
* Call by entering `setfact` anywhere

## Settings file
* Must be in the same folder as `setfact`
* See the sample `settings.json` file below
  * "(optional)" means the key, value pair is not required. The text "(optional)" should not be included in the actual settings file
  * Windows file paths must have the backslashes escaped (e.g. "c:\Users\project" would become "c:\\Users\\project")
* `<command-text>` can contain the following special commands:
  * `PROMPT#<prompt-key`: This command string in the `commandList` will prompt the user using the `<prompt-text` corresponding to the `<prompt-key`. The user's response will be stored and made available via the special substitution sequence `{{<prompt-key>}}` anytime within the same `commandList` or future commandLists that get executing later in the `commandSequence`
  * `WINSSH`: Handles SSH for Windows. The following command must be "<remote-server> \"<command-to-execute-on-remote-server>\""
  * `WINSCP`: Handles SCP for Windows. The following 3 commands must be: "<path-to-source-file>", "<remote-server>", "<path-to-dest-on-remote-server".
  * For further examples, please see the sample settings.json file included in the source.

```
{
  "projects": {
    <project-key>: {
      "name": <project-name>
      "path": {
        "Windows": <path-to-project>
        "Linux": <path-to-project>
      }
    }
  },
  "commands": {
    <command-key>: {
      "projectId (optional)": <project-key>,
      "name (optional)": <command-name-to-output-when-executing>
      "commandList": {
        "Windows": <command-text>,
        "Linux": <command-text>
      }
    }
  },
  "prompts": {
    <prompt-key>: {
      "text": <prompt-text>
    }
  },
  "modes": [
    {
      "name": <mode-name>,
      "tasks": [
        "name": <task-name>,
        "commandSequence": [<command-key>, <command-key>]
      ]
    }
  ],
}
```
